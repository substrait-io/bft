from typing import Dict, List, NamedTuple

from bft.cases.types import Case, CaseLiteral, Literal, case_to_kernel_str
from bft.core.function import Kernel


class DialectKernel(NamedTuple):
    arg_types: List[str]
    result_type: str


class DialectFunction(NamedTuple):
    name: str
    local_name: str
    infix: bool
    required_options: Dict[str, str]
    unsupported_kernels: List[DialectKernel]


class DialectFile(NamedTuple):
    name: str
    type: str
    scalar_functions: List[DialectFunction]


class SqlMapping(NamedTuple):
    local_name: str
    infix: bool
    should_pass: bool
    reason: str


class Dialect(object):
    def __init__(self, dialect_file: DialectFile):
        self.name = dialect_file.name
        self.__scalar_functions_by_name: Dict[str, DialectFunction] = {
            f.name: f for f in dialect_file.scalar_functions
        }

    def __supports_case_kernel(
        self,
        dfunc: DialectFunction,
        args: List[CaseLiteral],
        result: CaseLiteral | Literal["error", "undefined"],
    ):
        for unsupported_kernel in dfunc.unsupported_kernels:
            if len(unsupported_kernel.arg_types) != len(args):
                raise Exception(
                    "Unreachable path.  Unsupported kernel with different # of types than case"
                )
            matched = True
            for ktype, arg in zip(unsupported_kernel.arg_types, args):
                if arg.type != ktype:
                    matched = False
                    break
            if matched:
                if (
                    hasattr(result, "type")
                    and unsupported_kernel.result_type != result.type
                ):
                    raise Exception(
                        "Unreachable path.  Unsupported kernel matches arg types but not result type"
                    )
                return f"The dialect {self.name} does not support the kernel {case_to_kernel_str(dfunc.name, args, result)}"
        return None

    def __supports_options(self, dfunc: DialectFunction, case: Case):
        for case_opt, case_val in case.options:
            dval = dfunc.required_options.get(case_opt)
            if dval is None:
                return f"The dialect {self.name} does not describe how it handles the option {case_opt}"
            if dval != case_val:
                return f"The dialect {self.name} expects {case_opt}={dval} but {case_opt}={case_val} was requested"
        return None

    def required_options(self, function_name) -> Dict[str, str]:
        dfunc = self.__scalar_functions_by_name[function_name]
        return dfunc.required_options

    def supports_kernel(self, function_name: str, kernel: Kernel) -> bool:
        dfunc = self.__scalar_functions_by_name.get(function_name, None)
        if dfunc is None:
            return False
        for unsupported_kernel in dfunc.unsupported_kernels:
            if len(unsupported_kernel.arg_types) != len(kernel.arg_types):
                raise Exception(
                    "Unreachable path.  Unsupported kernel with different # of types than official kernel"
                )
            matched = True
            for ktype, arg_type in zip(unsupported_kernel.arg_types, kernel.arg_types):
                if arg_type != ktype:
                    matched = False
                    break
            if matched:
                return False
        return True

    def mapping_for_case(self, case: Case) -> SqlMapping:
        dfunc = self.__scalar_functions_by_name.get(case.function, None)
        if dfunc is None:
            return None

        kernel_failure = self.__supports_case_kernel(dfunc, case.args, case.result)
        if kernel_failure is not None:
            return SqlMapping(dfunc.local_name, dfunc.infix, False, kernel_failure)

        option_failure = self.__supports_options(dfunc, case)
        if option_failure is not None:
            return SqlMapping(dfunc.local_name, dfunc.infix, False, option_failure)

        return SqlMapping(dfunc.local_name, dfunc.infix, True, None)


class DialectsLibrary(object):
    def __init__(self, dialects: List[DialectFile]):
        self.dialects = {dialect.name: Dialect(dialect) for dialect in dialects}

    def get_dialect_by_name(self, name: str) -> Dialect:
        return self.dialects[name]
