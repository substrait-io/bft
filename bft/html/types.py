from typing import Dict, List, Literal, NamedTuple

from bft.core.function import Kernel


class FunctionOptionValueInfo(NamedTuple):
    # The name of the value
    # Sourced from Substrait YAML
    name: str
    # Description of the option
    # Sourced from BFT markdown
    description: str


# An option that can control function behavior
class FunctionOptionInfo(NamedTuple):
    # The name of the option
    # Sourced from Substrait YAML
    name: str
    # Description of the option
    # Sourced from Substrait YAML
    # Can be overridden by BFT markdown
    description: str
    # Possible values for the option
    # Sourced from Substrait YAML
    values: List[FunctionOptionValueInfo]


# Information about how the function behaves in different dialects
class FunctionDialectInfo(NamedTuple):
    # Name of the dialect (e.g. sqlite)
    # Sourced from dialect files
    name: str
    # Required options for this function in the given dialect
    # Sourced from Substrait YAML
    options: Dict[str, str]
    case_info: List[str]
    kernel_info: List[bool]


# Additional details or motivation for the function
class FunctionDetailInfo(NamedTuple):
    # Title of the detail section
    # Sourced from BFT markdown
    title: str
    # Body of the detail section
    # Sourced from BFT markdown
    description: str


# Invariants that the function respects
# Mostly useful for property-based testing
class FunctionPropertyInfo(NamedTuple):
    # The name of the invariant
    # Sourced from BFT markdown
    id: str
    # A description of the invariant
    # Sourced from BFT markdown
    description: str


class FunctionExampleResultInfo(NamedTuple):
    # Value of the result
    # Sourced from case files
    value: str


class FunctionExampleCaseInfo(NamedTuple):
    # Arguments to the function for this test case
    # Sourced from case files
    args: List[str]
    # Options values for this function
    # Sourced from case files
    options: List[str]
    # Result of the function run on the args
    # Sourced from case files
    result: Literal["error"] | Literal["undefined"] | FunctionExampleResultInfo


class FunctionExampleGroupInfo(NamedTuple):
    # Description of the example group
    # Sourced from case files
    description: str
    # Argument types for the examples in the group
    # Sourced from case files
    arg_types: List[str]
    # Names of options used in the examples in this group
    # Sourced from case files
    option_names: List[str]
    # Result type for the examples in the group
    # Sourced from case files
    result_type: str
    # Example executions
    cases: List[FunctionExampleCaseInfo]


# Information describing a function
class FunctionInfo(NamedTuple):
    # Name of the function (e.g. add)
    # Sourced from Substrait YAML
    name: str
    # The Substrait URI for the function (e.g. https://github.com/substrait-io/substrait/blob/main/extensions/functions_arithmetic.yaml)
    # Sourced from Substrait YAML
    # Can be overridden by BFT markdown
    uri: str
    # The last part of the URI (e.g. functions_arithmetic.yaml)
    # Sourced from Substrait YAML
    uri_short: str
    # A very brief (ideally one sentence) description of the function
    # Sourced from Substrait YAML
    brief: str
    # Available options for the function
    options: List[FunctionOptionInfo]
    # Available kernels for the function
    kernels: List[Kernel]
    # Dialect info for the function
    dialects: List[FunctionDialectInfo]
    # Function details
    details: List[FunctionDetailInfo]
    # Properties that hold true for the function
    properties: List[FunctionPropertyInfo]
    # Example function executions
    example_groups: List[FunctionExampleGroupInfo]


class FunctionIndexItem(NamedTuple):
    # Name of the function
    name: str
    # Summary of the function, sourced from Substrait YAML
    brief: str
    # Function category, i.e. Arithmetic, String, etc.
    category: str


class FunctionIndexInfo(NamedTuple):
    functions: List[FunctionIndexItem]
