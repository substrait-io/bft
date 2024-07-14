from bft.core.yaml_parser import BaseYamlParser, BaseYamlVisitor
from bft.dialects.types import DialectFile, DialectFunction, DialectKernel, short_type_to_type


class DialectFileVisitor(BaseYamlVisitor[DialectFile]):
    @staticmethod
    def visit_kernel(kernel):
        arg_types = [DialectFileVisitor.get_long_type(arg_type) for arg_type in kernel.split("_")]
        return DialectKernel(arg_types, any)

    @staticmethod
    def get_long_type(short_type):
        long_type = short_type_to_type.get(short_type, None)
        if long_type is None:
            return short_type
        return long_type

    @staticmethod
    def _get_unqualified_func_name(name):
        return name.split(".")[-1]

    def visit_scalar_function(self, func):
        return self._visit_function(func)

    def visit_aggregate_function(self, func):
        return self._visit_function(func)

    def _visit_function(self, func):
        name = self._get_or_die(func, "name")
        required_opts = self._get_or_else(func, "required_options", {})
        local_name = self._get_or_else(func, "local_name", self._get_unqualified_func_name(name))
        infix = self._get_or_else(func, "infix", False)
        postfix = self._get_or_else(func, "postfix", False)
        between = self._get_or_else(func, "between", False)
        aggregate = self._get_or_else(func, "aggregate", False)
        unsupported = self._get_or_else(func, "unsupported", False)
        # The extract function uses a special grammar in some SQL dialects.
        # i.e. SELECT EXTRACT(YEAR FROM times) FROM my_table
        extract = self._get_or_else(func, "extract", False)
        # bad_kernels = self._visit_list(self.visit_kernel, func, "unsupported_kernels")
        good_kernels = self._visit_list(self.visit_kernel, func, "supported_kernels")
        variadic_min = self._get_or_else(func, "variadic", -1)
        return DialectFunction(
            name,
            local_name,
            infix,
            postfix,
            between,
            aggregate,
            unsupported,
            extract,
            required_opts,
            variadic_min,
            good_kernels,
        )

    def visit(self, dfile):
        name = self._get_or_die(dfile, "name")
        dtype = self._get_or_die(dfile, "type")
        scalar_functions = self._visit_list(
            self.visit_scalar_function, dfile, "scalar_functions"
        )
        aggregate_functions = self._visit_list(
            self.visit_aggregate_function, dfile, "aggregate_functions"
        )
        uri_to_func_prefix = {uri: func_prefix for func_prefix, uri in dfile.get("dependencies", {}).items()}
        return DialectFile(name, dtype, scalar_functions, aggregate_functions, uri_to_func_prefix)


class DialectFileParser(BaseYamlParser[DialectFile]):
    def get_visitor(self) -> DialectFileVisitor:
        return DialectFileVisitor()
