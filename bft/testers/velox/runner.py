import pyvelox.pyvelox as pv

from bft.cases.runner import Case, SqlCaseResult, SqlCaseRunner, SqlMapping
from bft.dialects.types import Dialect


def is_type_supported(type):
    return type in set({"i64", "fp64", "boolean"})


class VeloxRunner(SqlCaseRunner):
    def __init__(self, dialect: Dialect):
        super().__init__(dialect)

    def run_sql_case(self, case: Case, mapping: SqlMapping) -> SqlCaseResult:
        arg_vectors = []
        arg_names = []
        for arg_idx, arg in enumerate(case.args):
            if not is_type_supported(arg.type):
                return SqlCaseResult.unsupported(
                    f"The type {arg.type} is not supported"
                )
            arg_vectors.append(pv.from_list([arg.value]))
            arg_names.append(f"arg{arg_idx}")
        if mapping.infix:
            if len(case.args) != 2:
                raise Exception(f"Infix function with {len(case.args)} args")
            expr_str = f"arg0 {mapping.local_name} arg1"
        else:
            joined_args = ", ".join(arg_names)
            expr_str = f"{mapping.local_name}({joined_args})"

        try:
            expr = pv.Expression.from_string(expr_str)
            answer = expr.evaluate(arg_names, arg_vectors)
            result = [v for v in answer]
        except RuntimeError as err:
            return SqlCaseResult.error(str(err))

        if len(result) != 1:
            raise Exception("Scalar function with one row output more than one row")
        result = result[0]

        if case.result == "undefined":
            return SqlCaseResult.success()
        elif case.result == "error":
            return SqlCaseResult.unexpected_pass(str(result))
        else:
            if result == case.result.value:
                return SqlCaseResult.success()
            else:
                return SqlCaseResult.mismatch(str(result))
