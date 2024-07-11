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
    def get_base_uri():
        return 'https://github.com/substrait-io/substrait/blob/main/extensions/'

    @staticmethod
    def get_supported_kernels_from_impls(func):
        supported_kernels = []
        for impl in func['impls']:
            signature = ""
            if 'args' in impl:
                for arg in impl['args']:
                    if 'value' in arg:
                        signature += arg['value'] + "_"
                    else:
                        debug(f"Missing value in arg: {arg['options']} for function: {func['name']}")
                        signature += 'string_'
                signature = signature[:-1]  # remove the last , from the signature
            # signature += ":" + impl['return']
            supported_kernels.append(signature)
        return supported_kernels

    @staticmethod
    def add_functions_to_map(func_list, function_map, suffix, extension):
        for func in func_list:
            name = func['name']
            uri = f"{suffix}.{name}"
            if name in function_map:
                debug(f"Duplicate function name: {name} renaming to {name}_{suffix} extension: {extension}")
                name = f"{name}_{suffix}"
                assert name not in function_map
            func['supported_kernels'] = Substrait.get_supported_kernels_from_impls(func)
            func['uri'] = uri
            func.pop('description', None)
            func.pop('impls', None)
            function_map[name] = func

    @staticmethod
    def read_substrait_extensions():
        # read files from substrait/extensions directory
        extensions = []
        for root, dirs, files in os.walk('substrait/extensions'):
            for file in files:
                if file.endswith('.yaml') and file.startswith('functions_'):
                    extensions.append(os.path.join(root, file))

        extensions.sort()

        scalar_functions = {}
        aggregate_functions = {}
        dependencies = {}
        # convert yaml file to a python dictionary
        for extension in extensions:
            suffix = extension[:-5]  # strip .yaml at the end of the extension
            suffix = suffix[suffix.rfind('/') + 1:]  # strip the path and get the name of the extension
            suffix = suffix[suffix.find('_') + 1:]  # get the suffix after the last _

            dependencies[suffix] = Substrait.get_base_uri() + extension
            with open(extension, 'r') as fh:
                data = yaml.load(fh, Loader=yaml.FullLoader)
                if 'scalar_functions' in data:
                    Substrait.add_functions_to_map(data['scalar_functions'], scalar_functions, suffix, extension)
                if 'aggregate_functions' in data:
                    Substrait.add_functions_to_map(data['aggregate_functions'], aggregate_functions, suffix, extension)

        return {'dependencies': dependencies, 'scalar_functions': scalar_functions, 'aggregate_functions': aggregate_functions}


class Dialect:
    @staticmethod
    def read_dialect(name):
        with open(f'dialects/{name}.yaml', 'r') as fh:
            data = yaml.load(fh, Loader=yaml.FullLoader)
        return data

    @staticmethod
    def get_unsupported_kernel_signatures(dialect_func):
        unsupported_kernels = []
        if 'unsupported_kernels' not in dialect_func:
            return unsupported_kernels

        for kernel in dialect_func['unsupported_kernels']:
            signature = ""
            for arg_type in kernel['args']:
                signature += arg_type + "_"
            signature = signature[:-1]  # remove the last _ from the signature
            # signature += ":" + kernel['result']
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
                func['name'] = substrait_functions[name]['uri']
            else:
                error(f"Function {name} not found in substrait functions")
            func.pop('unsupported_kernels', None)
            functions.append(func)
        return functions


def convert_dialect_to_allow_list(dialect, substrait_map):
    scalar_functions = []
    aggregate_functions = []
    if 'scalar_functions' in dialect:
        scalar_functions = Dialect.get_supported_functions_with_supported_kernels(
            dialect['scalar_functions'], substrait_map['scalar_functions'])
    if 'aggregate_functions' in dialect:
        aggregate_functions = Dialect.get_supported_functions_with_supported_kernels(
            dialect['aggregate_functions'], substrait_map['aggregate_functions'])
    dialect.pop('scalar_functions', None)
    dialect.pop('aggregate_functions', None)
    dialect['dependencies'] = substrait_map['dependencies']
    dialect['scalar_functions'] = scalar_functions
    dialect['aggregate_functions'] = aggregate_functions
    return dialect


def process_one_dialect(substrait_map, dialect_name):
    dialect_funcs = Dialect.read_dialect(dialect_name)
    dialect_funcs = convert_dialect_to_allow_list(dialect_funcs, substrait_map)
    print(
        f"{dialect_name} total scalar functions: {len(dialect_funcs['scalar_functions'])} "
        f"total aggregate functions: {len(dialect_funcs['aggregate_functions'])}")

    # dump the dialect functions with supported kernels to a file in the same order as in the dictionary
    with open(f'dialects_new/{dialect_name}.yaml', 'w') as fh:
        yaml_obj.dump(dialect_funcs, fh)


substrait_spec = Substrait.read_substrait_extensions()
print(
    f"Substrait total scalar functions: {len(substrait_spec['scalar_functions'])} "
    f"total aggregate functions: {len(substrait_spec['aggregate_functions'])}")
with open('out_substrait_funcs.yaml', 'w') as f:
    yaml_obj.dump(substrait_spec, f)

process_one_dialect(substrait_spec, 'cudf')
process_one_dialect(substrait_spec, 'datafusion')
process_one_dialect(substrait_spec, 'duckdb')
process_one_dialect(substrait_spec, 'postgres')
process_one_dialect(substrait_spec, 'snowflake')
process_one_dialect(substrait_spec, 'sqlite')
process_one_dialect(substrait_spec, 'velox_presto')
