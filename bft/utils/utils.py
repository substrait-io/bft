from typing import Dict


def type_to_dialect_type(type: str, type_map: Dict[str, str]):
    type_to_check = type.split("<")[0].strip() if "<" in type else type
    if type_to_check not in type_map:
        raise Exception(f"Unrecognized type: {type}")
    type_val = type_map[type_to_check]
    if not "<" in type:
        return type_val
    # transform parameterized type name to have dialect type
    return type.replace(type_to_check, type_val).replace("<", "(").replace(">", ")")
