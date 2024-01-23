import cudf
import math
import operator

from bft.cases.runner import SqlCaseResult, SqlCaseRunner
from bft.cases.types import Case, CaseLiteral
from bft.dialects.types import SqlMapping


type_map = {
    "i8": cudf.dtype("int8"),
    "i16": cudf.dtype("int16"),
    "i32": cudf.dtype("int32"),
    "i64": cudf.dtype("int64"),
    "fp32": cudf.dtype("float32"),
    "fp64": cudf.dtype("float64"),
    "boolean": cudf.dtype("bool"),
}


def type_to_cudf_dtype(type: str):
    if type not in type_map:
        raise Exception(f"Unrecognized type: {type}")
    return type_map[type]


class CudfRunner(SqlCaseRunner):
    def __init__(self, dialect):
        super().__init__(dialect)

    def run_sql_case(self, case: Case, mapping: SqlMapping) -> SqlCaseResult:
        arg_vectors = []
        arg_values = []
        for arg in case.args:
            dtype = type_to_cudf_dtype(arg.type)
            if dtype is None:
                return SqlCaseResult.unsupported(
                    f"The type {arg.type} is not supported"
                )
            arg_vectors.append(cudf.Series(arg.value, dtype=dtype))
            arg_values.append(arg.value)

        try:
            if len(arg_vectors) == 1:
                # Some functions that only take a single arg are able to be executed against
                # both a Series and a Dataframe whereas others are only able to be executed against a Dataframe.
                try:
                    gdf = cudf.DataFrame({"a": arg_values}, dtype=dtype)
                    result = gdf.eval(f"{mapping.local_name}(a)")
                except ValueError:
                    fn = getattr(arg_vectors[0], mapping.local_name)
                    result = fn()
            elif len(arg_vectors) == 2:
                if mapping.infix:
                    # If there are only Null/Nan/None values in the column, they are set to False instead of <NA>.
                    # We add extra data to ensure the <NA> value exists in the dataframe.
                    gdf = cudf.DataFrame(
                        {"a": [arg_values[0], True], "b": [arg_values[1], True]},
                        dtype=dtype,
                    )
                    result = gdf.eval(f"(a){mapping.local_name}(b)")
                else:
                    try:
                        fn = getattr(arg_vectors[0], mapping.local_name)
                        result = fn(arg_vectors[1])
                    except AttributeError:
                        fn = getattr(operator, mapping.local_name)
                        result = fn(arg_vectors[0], arg_vectors[1])
            else:
                fn = getattr(arg_vectors[0], mapping.local_name)
                try:
                    result = fn(arg_vectors[1:])
                except TypeError:
                    result = fn(arg_values[1], arg_values[2])
        except RuntimeError as err:
            return SqlCaseResult.error(str(err))

        if result.empty and (case.result.value is None or case.result.value is False):
            return SqlCaseResult.success()
        elif len(result) != 1 and not mapping.infix:
            raise Exception("Scalar function with one row output more than one row")
        else:
            result = result[0]

        if case.result == "undefined":
            return SqlCaseResult.success()
        elif case.result == "error":
            return SqlCaseResult.unexpected_pass(str(result))
        elif case.result == "nan":
            if math.isnan(result):
                return SqlCaseResult.success()
        else:
            if case.result.value == result:
                return SqlCaseResult.success()
            elif case.result.value == str(result):
                return SqlCaseResult.success()
            elif case.result.value is None:
                if str(result) == "<NA>":
                    return SqlCaseResult.success()
                elif result is None:
                    return SqlCaseResult.success()
                else:
                    return SqlCaseResult.mismatch(str(result))
            else:
                return SqlCaseResult.mismatch(str(result))
