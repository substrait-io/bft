import os
from typing import Dict, NamedTuple

import psycopg

from bft.cases.runner import SqlCaseResult, SqlCaseRunner
from bft.cases.types import Case, CaseLiteral
from bft.dialects.types import SqlMapping

type_map = {
    "i16": "smallint",
    "i32": "integer",
    "i64": "bigint",
    "fp32": "real",
    "fp64": "double precision",
    "boolean": "boolean",
}


def type_to_postgres_type(type: str):
    if type not in type_map:
        return None
    return type_map[type]


def literal_to_str(lit: CaseLiteral):
    if lit.value is None:
        return "null"
    return str(lit.value)


def get_connection_str():
    host = os.environ.get("POSTGRES_HOST", "localhost")
    dbname = os.environ.get("POSTGRES_DB", "bft")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    return f"{host=} {dbname=} {user=} {password=}"


class PostgresRunner(SqlCaseRunner):
    def __init__(self, dialect):
        super().__init__(dialect)
        self.conn = psycopg.connect(get_connection_str())

    def run_sql_case(self, case: Case, mapping: SqlMapping) -> SqlCaseResult:
        self.conn.execute("BEGIN;")

        try:
            arg_defs = []
            for idx, arg in enumerate(case.args):
                arg_type = type_to_postgres_type(arg.type)
                if arg_type is None:
                    return SqlCaseResult.unsupported(f"Unsupported type {arg.type}")
                arg_defs.append(f"arg{idx} {arg_type}")
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
        except psycopg.Error as err:
            return SqlCaseResult.error(str(err))
        finally:
            self.conn.rollback()
