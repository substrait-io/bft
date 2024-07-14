from typing import Dict, List, Literal, NamedTuple, Tuple


class CaseLiteral(NamedTuple):
    value: str | int | float | list
    type: str


class CaseGroup(NamedTuple):
    id: str
    description: str


class Case(NamedTuple):
    function: str
    base_uri: str
    group: CaseGroup
    args: List[CaseLiteral]
    result: CaseLiteral | Literal["error", "undefined"]
    options: List[Tuple[str, str]]


def case_to_kernel_str(
    function: str,
    args: List[CaseLiteral],
    result: CaseLiteral | Literal["error", "undefined"],
):
    joined_args = ", ".join([arg.type for arg in args])
    result_str = result
    if not isinstance(result_str, str):
        result_str = result.type
    return f"{function}({joined_args}) -> {result_str}"


class CaseFile(NamedTuple):
    function: str
    base_uri: str
    cases: List[Case]


class ProtoCase(NamedTuple):
    group: str
    args: List[CaseLiteral]
    result: CaseLiteral | Literal["error", "undefined"]
    options: Dict[str, str]
