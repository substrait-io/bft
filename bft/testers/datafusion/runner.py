import datafusion
import pyarrow as pa

from bft.cases.runner import SqlCaseResult, SqlCaseRunner
from bft.cases.types import Case, CaseLiteral
from bft.dialects.types import SqlMapping

type_map = {
    "i8": pa.int8(),
    "i16": pa.int16(),
    "i32": pa.int32(),
    "i64": pa.int64(),
    "fp32": pa.float32(),
    "fp64": pa.float64(),
    "boolean": pa.bool_(),
    "string": pa.string(),
}


def type_to_datafusion_type(type: str):
    if type not in type_map:
        raise Exception(f"Unrecognized type: {type}")
    return type_map[type]


def literal_to_str(lit: CaseLiteral):
    if lit.value is None:
        return "null"
    elif lit.value == "Null":
        return None
    elif lit.value == float("inf"):
        return "'Infinity'"
    elif lit.value == float("-inf"):
        return "'-Infinity'"
    return str(lit.value)


def is_string_type(arg):
    return (
        arg.type in ["string", "timestamp", "timestamp_tz", "date", "time"]
        or arg.value in ["Null"]
    ) and arg.value is not None


def arg_with_type(arg):
    if is_string_type(arg):
        arg_val = literal_to_str(arg)
    elif isinstance(arg.value, list) or arg.value is None:
        arg_val = None
    elif arg.type.startswith("i"):
        arg_val = int(arg.value)
    elif arg.type.startswith("fp"):
        arg_val = float(arg.value)
    else:
        arg_val = arg.value
    return arg_val


class DatafusionRunner(SqlCaseRunner):
    def __init__(self, dialect):
        super().__init__(dialect)
        self.ctx = datafusion.SessionContext()

    def run_sql_case(self, case: Case, mapping: SqlMapping) -> SqlCaseResult:

        try:
            arg_vectors = []
            arg_names = []
            arg_vals_list = []
            arg_types_list = []
            for arg_idx, arg in enumerate(case.args):
                arg_val = arg_with_type(arg)
                arg_type = type_to_datafusion_type(arg.type)
                arg_vals_list.append(arg_val)
                arg_types_list.append(arg_type)
                arg_names.append(f"arg{arg_idx}")

            if mapping.aggregate:
                arg_vectors = [pa.array(arg_vals_list, arg_type)]
                arg_names = [arg_names[0]]
            else:
                for val, arg_type in zip(arg_vals_list, arg_types_list):
                    arg_vectors.append(pa.array([val], arg_type))

            joined_arg_names = ",".join(arg_names)
            batch = pa.RecordBatch.from_arrays(
                arg_vectors,
                names=arg_names,
            )

            self.ctx.register_record_batches("my_table", [[batch]])
            if mapping.infix:
                if len(case.args) != 2:
                    raise Exception(f"Infix function with {len(case.args)} args")
                expr_str = f"SELECT {arg_names[0]} {mapping.local_name} {arg_names[1]} FROM my_table;"
            elif mapping.postfix:
                if len(arg_names) != 1:
                    raise Exception(f"Postfix function with {len(arg_names)} args")
                expr_str = f"SELECT {arg_names[0]} {mapping.local_name} FROM my_table;"
            elif mapping.aggregate:
                if len(arg_names) < 1:
                    raise Exception(f"Aggregate function with {len(arg_names)} args")
                expr_str = f"SELECT {mapping.local_name}({arg_names[0]}) FROM my_table;"
            else:
                expr_str = (
                    f"SELECT {mapping.local_name}({joined_arg_names}) FROM my_table;"
                )

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
        # except datafusion.Error as err:
        #     return SqlCaseResult.error(str(err))
        finally:
            self.ctx.deregister_table("my_table")
