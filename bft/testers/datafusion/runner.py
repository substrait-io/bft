import datafusion
import pyarrow

from bft.cases.runner import SqlCaseResult, SqlCaseRunner
from bft.cases.types import Case, CaseLiteral
from bft.dialects.types import SqlMapping

def is_type_supported(type):
    return type in set({"i64", "fp64", "boolean", "string"})

# type_map = {
#     "i8": "TINYINT",
#     "i16": "SMALLINT",
#     "i32": "INTEGER",
#     "i64": "BIGINT",
#     "fp32": "REAL",
#     "fp64": "DOUBLE",
#     "boolean": "BOOLEAN",
#     "string": "VARCHAR",
# }
#
#
# def type_to_datafusion_type(type: str):
#     if type not in type_map:
#         raise Exception(f"Unrecognized type: {type}")
#     return type_map[type]


class DatafusionRunner(SqlCaseRunner):
    def __init__(self, dialect):
        super().__init__(dialect)
        self.ctx = datafusion.SessionContext()

    def run_sql_case(self, case: Case, mapping: SqlMapping) -> SqlCaseResult:

        try:
            arg_vectors = []
            arg_names = []
            for arg_idx, arg in enumerate(case.args):
                if not is_type_supported(arg.type):
                    return SqlCaseResult.unsupported(
                        f"The type {arg.type} is not supported"
                    )
                arg_vectors.append(pyarrow.array([arg.value]))
                arg_names.append(f"arg{arg_idx}")

            joined_arg_names = ",".join(arg_names)
            batch = pyarrow.RecordBatch.from_arrays(arg_vectors, names=arg_names,)

            self.ctx.register_record_batches('my_table', [[batch]])
            if mapping.infix:
                if len(case.args) != 2:
                    raise Exception(f"Infix function with {len(case.args)} args")
                expr_str = f"SELECT {arg_names[0]} {mapping.local_name} {arg_names[1]} FROM my_table;"
            elif mapping.postfix:
                if len(arg_names) != 1:
                    raise Exception(f"Postfix function with {len(arg_names)} args")
                expr_str = f"SELECT {arg_names[0]} {mapping.local_name} FROM my_table;"
            else:
                expr_str = f"SELECT {mapping.local_name}({joined_arg_names}) FROM my_table;"

            result = self.ctx.sql(expr_str).collect()[0].columns[0].to_pylist()

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
        except datafusion.Error as err:
            return SqlCaseResult.error(str(err))
        finally:
            self.ctx.deregister_table("my_table")