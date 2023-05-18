import duckdb
from typing import Dict, NamedTuple

from bft.cases.runner import SqlCaseResult, SqlCaseRunner
from bft.cases.types import Case, CaseLiteral
from bft.dialects.types import SqlMapping

type_map = {
    "i8": "TINYINT",
    "i16": "SMALLINT",
    "i32": "INTEGER",
    "i64": "BIGINT",
    "fp32": "REAL",
    "fp64": "DOUBLE",
    "boolean": "BOOLEAN",
    "string": "VARCHAR"
}


def type_to_duckdb_type(type: str):
    if type not in type_map:
        raise Exception(f"Unrecognized type: {type}")
    return type_map[type]


def literal_to_str(lit: CaseLiteral):
    if lit.value is None:
        return "null"
    elif lit.value == float("inf"):
        return "'Infinity'"
    elif lit.value == float("-inf"):
        return "'-Infinity'"
    return str(lit.value)


class DuckDBRunner(SqlCaseRunner):
    def __init__(self, dialect):
        super().__init__(dialect)
        self.conn = duckdb.connect()

    def run_sql_case(self, case: Case, mapping: SqlMapping) -> SqlCaseResult:

        try:
            arg_defs = [
                f"arg{idx} {type_to_duckdb_type(arg.type)}"
                for idx, arg in enumerate(case.args)
            ]
            schema = ",".join(arg_defs)
            self.conn.execute(f"CREATE TABLE my_table({schema});")

            arg_names = [f"arg{idx}" for idx in range(len(case.args))]
            joined_arg_names = ",".join(arg_names)
            arg_vals = ",".join([literal_to_str(arg) for arg in case.args])
            self.conn.execute(
                f"INSERT INTO my_table ({joined_arg_names}) VALUES ({arg_vals});"
            )

            if mapping.infix:
                if len(arg_names) != 2:
                    raise Exception(f"Infix function with {len(arg_names)} args")
                expr = f"SELECT {arg_names[0]} {mapping.local_name} {arg_names[1]} FROM my_table;"
            elif mapping.postfix:
                if len(arg_names) != 1:
                    raise Exception(f"Postfix function with {len(arg_names)} args")
                expr = f"SELECT {arg_names[0]} {mapping.local_name} FROM my_table;"
            else:
                expr = f"SELECT {mapping.local_name}({joined_arg_names}) FROM my_table;"
            result = self.conn.execute(expr).fetchone()[0]

            if case.result == "undefined":
                return SqlCaseResult.success()
            elif case.result == "error":
                return SqlCaseResult.unexpected_pass(str(result))
            else:
                if result == case.result.value:
                    return SqlCaseResult.success()
                else:
                    return SqlCaseResult.mismatch(str(result))
        except duckdb.Error as err:
            return SqlCaseResult.error(str(err))
        finally:
            self.conn.execute("DROP TABLE my_table")
