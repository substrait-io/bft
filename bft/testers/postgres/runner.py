import datetime
import math
import os

import psycopg

from bft.cases.runner import SqlCaseResult, SqlCaseRunner
from bft.cases.types import Case
from bft.dialects.types import SqlMapping

type_map = {
    "i16": "smallint",
    "i32": "integer",
    "i64": "bigint",
    "fp32": "float4",
    "fp64": "float8",
    "boolean": "boolean",
    "string": "text",
    "date": "date",
    "time": "time",
    "timestamp": "timestamp",
    "timestamp_tz": "timestamptz",
    "interval": "interval",
}


def type_to_postgres_type(type: str):
    if type not in type_map:
        return None
    return type_map[type]


def literal_to_str(lit: str | int | float):
    if lit is None:
        return "null"
    elif lit in [float("inf"), "inf"]:
        return "'Infinity'"
    elif lit in [float("-inf"), "-inf"]:
        return "'-Infinity'"
    return str(lit)


def is_string_type(arg):
    return (
        arg.type in ["string", "timestamp", "timestamp_tz", "date", "time"]
        and arg.value is not None
    )


def is_datetype(arg):
    print(f"postgres type is: {type(arg)}")
    return type(arg) in [datetime.datetime, datetime.date, datetime.timedelta]


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
            arg_vals_list = list()
            for arg in case.args:
                if is_string_type(arg):
                    arg_vals_list.append("'" + literal_to_str(arg.value) + "'")
                else:
                    arg_vals_list.append(literal_to_str(arg.value))
            arg_vals = ", ".join(arg_vals_list)
            if mapping.aggregate:
                arg_vals_list = list()
                for arg in case.args:
                    arg_vals = ""
                    for value in arg.value:
                        if is_string_type(arg):
                            if value:
                                arg_vals += f"('{literal_to_str(value)}'),"
                            else:
                                arg_vals += f"({literal_to_str(value)}),"
                        else:
                            arg_vals += f"({literal_to_str(value)}),"
                    arg_vals_list.append([arg_vals[:-1]])
                for arg_name, arg_vals in zip(arg_names, arg_vals_list):
                    if len(arg_vals[0]):
                        self.conn.execute(
                            f"INSERT INTO my_table ({arg_name}) VALUES {arg_vals[0]};"
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
            elif mapping.extract:
                if len(arg_names) != 2:
                    raise Exception(f"Extract function with {len(arg_names)} args")
                expr = f"SELECT {mapping.local_name}({arg_vals_list[0]} FROM {arg_names[1]}) FROM my_table;"
            elif mapping.between:
                if len(arg_names) != 3:
                    raise Exception(f"Between function with {len(arg_names)} args")
                expr = f"SELECT {arg_names[0]} BETWEEN {arg_names[1]} AND {arg_names[2]} FROM my_table;"
            elif mapping.local_name == 'count(*)':
                if len(arg_names) < 1:
                    raise Exception(f"Aggregate function with {len(arg_names)} args")
                expr = f"SELECT {mapping.local_name} FROM my_table;"
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
            elif case.result == "nan":
                print(f"Expected NAN but received {result}")
                return SqlCaseResult.error(str(result))
            # Issues with python float comparison:
            # https://tutorpython.com/python-mathisclose/#The_problem_with_using_for_float_comparison
            # https://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python
            elif case.result.type.startswith("fp") and case.result.value:
                if math.isclose(result, case.result.value, rel_tol=1e-7):
                    return SqlCaseResult.success()
            else:
                if result == case.result.value:
                    return SqlCaseResult.success()
                elif is_datetype(result) and str(result) == case.result.value:
                    return SqlCaseResult.success()
                else:
                    return SqlCaseResult.mismatch(str(result))
        except psycopg.Error as err:
            return SqlCaseResult.error(str(err))
        finally:
            self.conn.rollback()
