from typing import Dict, List, NamedTuple


class BasicSupplement(NamedTuple):
    title: str
    description: str


class OptionSupplement(NamedTuple):
    description: str
    values: List[BasicSupplement]


class SupplementsFile(NamedTuple):
    function: str
    dir_path: str
    options: Dict[str, OptionSupplement]
    details: List[BasicSupplement]
    properties: List[BasicSupplement]


def empty_supplements_file(function_name: str):
    return SupplementsFile(function_name, "", {}, [], [])
