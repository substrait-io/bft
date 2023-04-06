from typing import Dict, NamedTuple

import cudf

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
}


def type_to_cudf_dtype(type: str):
    if type not in type_map:
        raise Exception(f"Unrecognized type: {type}")
    return type_map[type]


def literal_to_str(lit: CaseLiteral):
    return str(lit.value)


class CudfRunner(SqlCaseRunner):
    def __init__(self, dialect):
        super().__init__(dialect)

    def run_sql_case(self, case: Case, mapping: SqlMapping) -> SqlCaseResult:
        arg_vectors = []
        for arg in case.args:
            dtype = type_to_cudf_dtype(arg.type)
            if dtype is None:
                return SqlCaseResult.unsupported(
                    f"The type {arg.type} is not supported"
                )
            arg_vectors.append(cudf.Series(arg.value, dtype=dtype))
        if mapping.infix:
            raise Exception("Cudf runner does not understand infix mappings")

        fn = getattr(arg_vectors[0], mapping.local_name)

        try:
            if len(arg_vectors) == 1:
                result = fn()
            elif len(arg_vectors) == 2:
                result = fn(arg_vectors[1])
            else:
                result = fn(arg_vectors[1:])
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
