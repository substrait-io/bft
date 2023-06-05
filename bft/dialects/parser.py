from bft.core.yaml_parser import BaseYamlParser, BaseYamlVisitor
from bft.dialects.types import DialectFile, DialectFunction, DialectKernel


class DialectFileVisitor(BaseYamlVisitor[DialectFile]):
    def visit_kernel(self, kernel):
        arg_types = self._get_or_die(kernel, "args")
        result_type = self._get_or_die(kernel, "result")
        return DialectKernel(arg_types, result_type)

    def visit_scalar_function(self, func):
        name = self._get_or_die(func, "name")
        required_opts = self._get_or_else(func, "required_options", {})
        local_name = self._get_or_else(func, "local_name", name)
        infix = self._get_or_else(func, "infix", False)
        postfix = self._get_or_else(func, "postfix", False)
        aggregate = self._get_or_else(func, "aggregate", False)
        unsupported = self._get_or_else(func, "unsupported", False)
        # The extract function uses a special grammar in some SQL dialects.
        # i.e. SELECT EXTRACT(YEAR FROM times) FROM my_table
        extract = self._get_or_else(func, "extract", False)
        bad_kernels = self._visit_list(self.visit_kernel, func, "unsupported_kernels")
        return DialectFunction(
            name,
            local_name,
            infix,
            postfix,
            unsupported,
            extract,
            aggregate,
            required_opts,
            bad_kernels,
        )

    def visit_aggregate_function(self, func):
        name = self._get_or_die(func, "name")
        required_opts = self._get_or_else(func, "required_options", {})
        local_name = self._get_or_else(func, "local_name", name)
        infix = self._get_or_else(func, "infix", False)
        postfix = self._get_or_else(func, "postfix", False)
        aggregate = self._get_or_else(func, "aggregate", False)
        unsupported = self._get_or_else(func, "unsupported", False)
        bad_kernels = self._visit_list(self.visit_kernel, func, "unsupported_kernels")
        return DialectFunction(
            name,
            local_name,
            infix,
            postfix,
            aggregate,
            unsupported,
            required_opts,
            bad_kernels,
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
        return DialectFile(name, dtype, scalar_functions, aggregate_functions)


class DialectFileParser(BaseYamlParser[DialectFile]):
    def get_visitor(self) -> DialectFileVisitor:
        return DialectFileVisitor()
