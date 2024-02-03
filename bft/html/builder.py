import pathlib
import re
from typing import Dict, List, MutableSet, NamedTuple

import yaml
from jinja2 import Environment, PackageLoader, select_autoescape

from bft.cases.loader import load_cases
from bft.cases.types import Case
from bft.core.function import FunctionDefinition, Kernel, Option
from bft.core.index_parser import IndexFunctionsFile, load_index
from bft.dialects.loader import load_dialects
from bft.dialects.types import Dialect, DialectsLibrary
from bft.html.types import (
    FunctionIndexInfo,
    FunctionIndexItem,
    ScalarFunctionDetailInfo,
    ScalarFunctionDialectInfo,
    ScalarFunctionExampleCaseInfo,
    ScalarFunctionExampleGroupInfo,
    ScalarFunctionInfo,
    ScalarFunctionOptionInfo,
    ScalarFunctionOptionValueInfo,
    ScalarFunctionPropertyInfo,
)
from bft.substrait.extension_file_parser import (
    ExtensionFileParser,
    LibraryBuilder,
    add_extensions_file_to_library,
)
from bft.supplements.parser import load_supplements
from bft.supplements.types import (
    BasicSupplement,
    OptionSupplement,
    SupplementsFile,
    empty_supplements_file,
)

env = Environment(loader=PackageLoader("bft"), autoescape=select_autoescape())

scalar_func_template = env.get_template("scalar_function.j2")
function_index_template = env.get_template("function_index.j2")


def render_scalar_function(info: ScalarFunctionInfo):
    return scalar_func_template.render(info._asdict())


def render_function_index(info: FunctionIndexInfo):
    return function_index_template.render(info._asdict())

def replace_pattern_sequences(content, dir_path):
    pattern = re.compile(r'/\[%([\w\s]+)\$([\w\s]+)%\]')
    matches = re.finditer(pattern, content)

    # If no pattern sequences are found, no need to load YAML
    if not any(matches):
        return content

    # Check if definition file exists
    def_path = dir_path + "/definitions.yml"
    if not pathlib.Path(def_path).is_file():
        raise FileNotFoundError(f"Definitions file '{def_path}' not found while"
                                "supplemental file requires it.")

    # Load YAML file
    with open(def_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)

    # Search and replace pattern sequences
    matches = re.finditer(pattern, content)
    for match in matches:
        field_name, property_name = match.groups()
        property_value = data.get(field_name, {}).get(property_name)

        if property_value is not None:
            content = content.replace(match.group(0), str(property_value))
        else:
            print(f"Warning: Field '{field_name}' or Property '{property_name}' not found in the definitions file.")

    return content

def create_function_option_value(
    val: str, supplement: OptionSupplement, dir_path: str
) -> ScalarFunctionOptionValueInfo:
    name = val
    if supplement is None:
        matching_sup = []
    else:
        matching_sup = [v for v in supplement.values if v.title == val]
    if len(matching_sup) == 0:
        description = "Missing supplementary description"
    else:
        description = replace_pattern_sequences(matching_sup[0].description, dir_path)
    return ScalarFunctionOptionValueInfo(name, description)


def create_function_option(
    opt: Option, supplement: SupplementsFile
) -> ScalarFunctionOptionInfo:
    name = opt.name
    opt_supp = supplement.options.get(name, None)
    if opt_supp is None:
        description = f"No supplemental information for {name}"
    else:
        description = replace_pattern_sequences(opt_supp.description, supplement.dir_path)
    values = [create_function_option_value(val, opt_supp, supplement.dir_path) for val in opt.values]
    return ScalarFunctionOptionInfo(name, description, values)


def create_examples(cases: List[Case]) -> List[ScalarFunctionExampleCaseInfo]:
    examples: List[ScalarFunctionExampleCaseInfo] = []
    for case in cases:
        arg_vals = [arg.value for arg in case.args]
        opt_vals = [opt[1] for opt in case.options]
        result = case.result
        examples.append(ScalarFunctionExampleCaseInfo(arg_vals, opt_vals, result))
    return examples


def create_example_groups(cases: List[Case]) -> List[ScalarFunctionExampleGroupInfo]:
    groups: Dict[str, Case] = {}
    for case in cases:
        # This may clobber previous insertions.  We just need one prototypical case per group
        # Prefer a case that actually has a typed result if possible
        if case.group.id not in groups or hasattr(case.result, "type"):
            groups[case.group.id] = case

    example_groups: List[ScalarFunctionExampleGroupInfo] = []
    ordered_cases: List[Case] = []
    for group_id in sorted(groups.keys()):
        protocase = groups[group_id]
        arg_types = [arg.type for arg in protocase.args]
        opt_names = [opt[0] for opt in protocase.options]
        if hasattr(protocase.result, "type"):
            result_type = protocase.result.type
        else:
            result_type = protocase.result
        group_cases = [c for c in cases if c.group.id == group_id]
        for case in group_cases:
            ordered_cases.append(case)
        examples = create_examples(group_cases)
        description = protocase.group.description
        example_groups.append(
            ScalarFunctionExampleGroupInfo(
                description, arg_types, opt_names, result_type, examples
            )
        )
    return example_groups, ordered_cases


def create_detail(detail: BasicSupplement) -> ScalarFunctionDetailInfo:
    title = detail.title
    description = detail.description
    return ScalarFunctionDetailInfo(title, description)


def create_property(prop: BasicSupplement, dir_path: str) -> ScalarFunctionPropertyInfo:
    id = prop.title
    description = replace_pattern_sequences(prop.description, dir_path)
    return ScalarFunctionPropertyInfo(id, description)


def create_dialect(
    function: str, dialect: Dialect, cases: List[Case], kernels: List[Kernel]
) -> ScalarFunctionDialectInfo:
    name = dialect.name
    options = dialect.required_options(function)
    case_info = []
    for case in cases:
        mapping = dialect.mapping_for_case(case)
        if mapping is None:
            case_info.append("There is no dialect information for this function")
            continue
        case_info.append(mapping.reason)
    kernel_info = []
    for kernel in kernels:
        kernel_info.append(dialect.supports_kernel(function, kernel))
    return ScalarFunctionDialectInfo(name, options, case_info, kernel_info)


def create_function_info(
    func: FunctionDefinition,
    cases: List[Case],
    supplements: SupplementsFile,
    dialects: DialectsLibrary,
) -> ScalarFunctionInfo:
    name = "_".join(func.name.split('_')[1:])
    uri_short = func.uri
    uri = "https://github.com/substrait-io/substrait/blob/main/extensions/" + uri_short
    brief = func.description
    options = [create_function_option(opt, supplements) for opt in func.options]
    kernels = func.kernels
    example_groups, ordered_cases = create_example_groups(cases)

    dialects = [
        create_dialect(name, dialect, ordered_cases, func.kernels)
        for dialect in dialects.dialects.values()
    ]
    details = [create_detail(detail) for detail in supplements.details]
    properties = [create_property(prop, supplements.dir_path) for prop in supplements.properties]
    return ScalarFunctionInfo(
        name,
        uri,
        uri_short,
        brief,
        options,
        kernels,
        dialects,
        details,
        properties,
        example_groups,
    )


def create_function_index(
    functions: List[FunctionDefinition]
) -> FunctionIndexInfo:
    items = [
        FunctionIndexItem(
            function.name,
            function.description,
            function.uri.split('_')[1].split('.')[0].title()
        )
        for function in functions
    ]
    return FunctionIndexInfo(items)


def build_site(index_path: str, dest_dir):
    root = pathlib.Path(index_path).parent
    index_contents = load_index(index_path)
    library_builder = LibraryBuilder()
    for function_file in index_contents.function_files:
        resolved_location = (root / function_file.location).resolve()
        with open(resolved_location, "rb") as f:
            add_extensions_file_to_library(
                resolved_location, ExtensionFileParser().parse(f), library_builder
            )
    functions = library_builder.finish()

    cases: List[Case] = []
    for cases_dir in index_contents.case_directories:
        resolved_case_dir = (root / cases_dir).resolve()
        cases = cases + load_cases(resolved_case_dir)

    supplements: Dict[str, SupplementsFile] = {}
    for supplements_dir in index_contents.supplement_directories:
        supp_dir_resolved = (root / supplements_dir).resolve()
        print(f"Loading supplements from {supp_dir_resolved}")
        supplements.update(load_supplements(supp_dir_resolved))

    dialects_lib: DialectsLibrary = None
    for dialects_dir in index_contents.dialect_directories:
        resolved_dialects_dir = (root / dialects_dir).resolve()
        if dialects_lib is not None:
            raise Exception("Multiple dialect directories not yet implemented")
        dialects_lib = load_dialects(resolved_dialects_dir)

    print(
        f"There are {len(functions)} functions and {len(cases)} cases and {len(supplements)} supplements and {(len(dialects_lib.dialects))} dialects"
    )
    for func in functions:
        func_name_full = "_".join(func.name.split('_')[1:])
        matching_cases = [case for case in cases if case.function == func_name_full]
        supplement = supplements.get(func_name_full, None)
        if supplement is None:
            supplement = empty_supplements_file(func_name_full)
        print(f"Creating site for {func.name}")
        info = create_function_info(func, matching_cases, supplement, dialects_lib)
        out_path = pathlib.Path(dest_dir) / f"{func.name}.html"
        with open(out_path, mode="w") as out:
            out.write(render_scalar_function(info))

    function_index = create_function_index(functions)
    out_path = pathlib.Path(dest_dir) / f"index.html"
    with open(out_path, mode="w") as out:
        out.write(render_function_index(function_index))
