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
        bad_kernels = self._visit_list(self.visit_kernel, func, "unsupported_kernels")
        return DialectFunction(name, local_name, infix, required_opts, bad_kernels)

    def visit(self, dfile):
        name = self._get_or_die(dfile, "name")
        dtype = self._get_or_die(dfile, "type")
        scalar_functions = self._visit_list(
            self.visit_scalar_function, dfile, "scalar_functions"
        )
        return DialectFile(name, dtype, scalar_functions)


class DialectFileParser(BaseYamlParser[DialectFile]):
    def get_visitor(self) -> DialectFileVisitor:
        return DialectFileVisitor()
