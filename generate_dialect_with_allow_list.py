import os
import yaml
from ruamel.yaml import YAML

yaml_obj = YAML()
enable_debug = False


def error(msg):
    print(f"ERROR: {msg}")


def debug(msg):
    if enable_debug:
        print(f"DEBUG: {msg}")


class Substrait:

    @staticmethod
    def get_supported_kernels_from_impls(func):
        supported_kernels = []
        for impl in func['impls']:
            signature = ""
            if 'args' in impl:
                for arg in impl['args']:
                    if 'value' in arg:
                        signature += arg['value'] + ","
                    else:
                        debug(f"Missing value in arg: {arg['options']} for function: {func['name']}")
                        signature += 'string_'
                signature = signature[:-1]  # remove the last , from the signature
            signature += ":" + impl['return']
            supported_kernels.append(signature)
        return supported_kernels

    @staticmethod
    def add_functions_to_map(func_list, function_map, suffix, extension):
        for func in func_list:
            name = func['name']
            if name in function_map:
                debug(f"Duplicate function name: {name} renaming to {name}_{suffix} extension: {extension}")
                name = f"{name}_{suffix}"
                assert name not in function_map
            func['supported_kernels'] = Substrait.get_supported_kernels_from_impls(func)
            func.pop('description', None)
            func.pop('impls', None)
            function_map[name] = func

    @staticmethod
    def read_substrait_extensions():
        # read files from substrait/extensions directory
        extensions = []
        for root, dirs, files in os.walk('substrait/extensions'):
            for file in files:
                if file.endswith('.yaml'):
                    extensions.append(os.path.join(root, file))

        extensions.sort()

        scalar_functions = {}
        aggregate_functions = {}
        # convert yaml file to a python dictionary
        for extension in extensions:
            suffix = extension[:-5]  # strip .yaml at the end of the extension
            suffix = suffix[suffix.rfind('/') + 1:]  # strip the path and get the name of the extension
            suffix = suffix[suffix.rfind('_') + 1:]  # get the suffix after the last _

            with open(extension, 'r') as fh:
                data = yaml.load(fh, Loader=yaml.FullLoader)
                if 'scalar_functions' in data:
                    Substrait.add_functions_to_map(data['scalar_functions'], scalar_functions, suffix, extension)
                if 'aggregate_functions' in data:
                    Substrait.add_functions_to_map(data['aggregate_functions'], aggregate_functions, suffix, extension)

        return {'scalar_functions': scalar_functions, 'aggregate_functions': aggregate_functions}


class Dialect:
    @staticmethod
    def read_dialect(name):
        dialect = {}
        with open(f'dialects/{name}.yaml', 'r') as fh:
            data = yaml.load(fh, Loader=yaml.FullLoader)
            dialect['scalar_functions'] = data['scalar_functions']
            dialect['aggregate_functions'] = data['aggregate_functions']
        return dialect

    @staticmethod
    def get_unsupported_kernel_signatures(dialect_func):
        unsupported_kernels = []
        if 'unsupported_kernels' not in dialect_func:
            return unsupported_kernels

        for kernel in dialect_func['unsupported_kernels']:
            signature = ""
            for arg_type in kernel['args']:
                signature += arg_type + ","
            signature = signature[:-1]  # remove the last , from the signature
            signature += ":" + kernel['result']
            unsupported_kernels.append(signature)
        return unsupported_kernels

    @staticmethod
    def get_supported_kernels_in_func(dialect_func, substrait_func):
        supported_kernels = []
        unsupported_signatures_in_dialect = Dialect.get_unsupported_kernel_signatures(dialect_func)
        for signature in substrait_func['supported_kernels']:
            if signature not in unsupported_signatures_in_dialect:
                supported_kernels.append(signature)
        return supported_kernels

    @staticmethod
    def get_supported_functions_with_supported_kernels(dialect_funcs, substrait_functions):
        functions = []
        for func in dialect_funcs:
            name = func['name']
            if 'unsupported' in func and func['unsupported']:
                continue
            if name in substrait_functions:
                func['supported_kernels'] = Dialect.get_supported_kernels_in_func(func, substrait_functions[name])
            else:
                error(f"Function {name} not found in substrait functions")
            func.pop('unsupported_kernels', None)
            functions.append(func)
        return functions


def convert_dialect_to_allow_list(dialect_funcs, substrait_functions):
    if 'scalar_functions' in dialect_funcs:
        dialect_funcs['scalar_functions'] = Dialect.get_supported_functions_with_supported_kernels(
            dialect_funcs['scalar_functions'], substrait_functions['scalar_functions'])
    if 'aggregate_functions' in dialect_funcs:
        dialect_funcs['aggregate_functions'] = Dialect.get_supported_functions_with_supported_kernels(
            dialect_funcs['aggregate_functions'], substrait_functions['aggregate_functions'])
    return dialect_funcs


def process_one_dialect(substrait_functions, dialect_name):
    dialect_funcs = Dialect.read_dialect(dialect_name)
    dialect_funcs = convert_dialect_to_allow_list(dialect_funcs, substrait_functions)
    print(
        f"{dialect_name} total scalar functions: {len(dialect_funcs['scalar_functions'])} "
        f"total aggregate functions: {len(dialect_funcs['aggregate_functions'])}")

    # dump the dialect functions with supported kernels to a file in the same order as in the dictionary
    with open(f'out_{dialect_name}_funcs.yaml', 'w') as fh:
        yaml_obj.dump(dialect_funcs, fh)


substrait_funcs = Substrait.read_substrait_extensions()
print(
    f"Substrait total scalar functions: {len(substrait_funcs['scalar_functions'])} "
    f"total aggregate functions: {len(substrait_funcs['aggregate_functions'])}")
with open('out_substrait_funcs.yaml', 'w') as f:
    yaml_obj.dump(substrait_funcs, f)

process_one_dialect(substrait_funcs, 'duckdb')
