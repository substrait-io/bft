import sqlite3
from typing import Dict, NamedTuple

from bft.cases.runner import SqlCaseResult, SqlCaseRunner
from bft.cases.types import Case, CaseLiteral
from bft.dialects.types import SqlMapping

type_map = {
    "i8": "TINYINT",
    "i16": "SMALLINT",
    "i32": "INT",
    "i64": "HUGEINT",
    "fp32": "REAL",
    "fp64": "REAL",
    "boolean": "BOOLEAN",
}


def type_to_sqlite_type(type: str):
    if type not in type_map:
        raise Exception(f"Unrecognized type: {type}")
    return type_map[type]


def literal_to_str(lit: CaseLiteral):
    if lit.value is None:
        return "null"
    # The simplest way to get infinity into sqlite is to use an impossibly large/small value
    elif lit.value == float("inf"):
        return "9e999"
    elif lit.value == float("-inf"):
        return "-9e999"
    return str(lit.value)


class SqliteRunner(SqlCaseRunner):
    def __init__(self, dialect):
        super().__init__(dialect)
        self.conn = sqlite3.connect(":memory:")

    def run_sql_case(self, case: Case, mapping: SqlMapping) -> SqlCaseResult:
        self.conn.execute("BEGIN;")

        try:
            arg_defs = [
                f"arg{idx} {type_to_sqlite_type(arg.type)}"
                for idx, arg in enumerate(case.args)
            ]
            schema = ",".join(arg_defs)
            self.conn.execute(f"CREATE TABLE my_table({schema});")

            arg_names = [f"arg{idx}" for idx in range(len(case.args))]
            if mapping.aggregate:
                arg_names = [arg_names[0]]
            joined_arg_names = ",".join(arg_names)
            arg_vals = ",".join([literal_to_str(arg) for arg in case.args])
            if mapping.aggregate:
                arg_vals_list = ", ".join(f"({val})" for val in arg_vals.split(","))
                if arg_vals != "[]":
                    self.conn.execute(
                        f"INSERT INTO my_table ({joined_arg_names}) VALUES {arg_vals_list};"
                    )
            else:
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
            elif mapping.aggregate:
                if len(arg_names) < 1:
                    raise Exception(f"Aggregate function with {len(arg_names)} args")
                expr = f"SELECT {mapping.local_name}({arg_names[0]}) FROM my_table;"
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
        except sqlite3.Error as err:
            return SqlCaseResult.error(str(err))
        finally:
            self.conn.rollback()
