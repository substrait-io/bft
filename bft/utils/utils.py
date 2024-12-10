from typing import Dict
import datetime


def type_to_dialect_type(type: str, type_map: Dict[str, str])->str:
    """
    Convert a substrait type to a dialect type

    :param type: substrait name of base type (i.e. without parameters)
    :param type_map:map of substrait type to dialect base type (i.e. without parameters)
    :return:dialect type

    e.g. type_map: {"interval": "INTERVAL", "decimal": "NUMERIC"}
        input type: "decimal<37, 3>",  -> output: "NUMERIC(37, 3)"
    e.g. input type: "interval", output: "INTERVAL"

    in above example "decimal" or "interval" are referred as base type whereas decimal<37, 3> is parameterized type

    """
    type_to_check = type.split("<")[0].strip() if "<" in type else type
    if type_to_check not in type_map:
        return None
    type_val = type_map[type_to_check]
    if not "<" in type:
        return type_val
    # transform parameterized type name to have dialect type
    return type.replace(type_to_check, type_val).replace("<", "(").replace(">", ")")

def has_only_date(value: datetime.datetime):
    if (
        value.hour == 0
        and value.minute == 0
        and value.second == 0
        and value.microsecond == 0
    ):
        return True
    return False

def datetype_value_equal(result, case_result):
    if str(result) == case_result:
        return True
    if (
        isinstance(result, datetime.datetime)
        and has_only_date(result)
        and str(result.date()) == case_result
    ):
        return True
    return False
