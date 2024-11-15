import yaml
import os
from collections import defaultdict
from itertools import count
from tools.convert_tests.convert_tests_helper import convert_to_new_value


# Define a custom YAML loader that interprets all values as strings
def string_loader(loader, node):
    return str(loader.construct_scalar(node))


def list_of_decimal_constructor(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode):
    return [string_loader(loader, item) for item in node.value]


def load_test_file(file_path):
    """Load a YAML file, interpreting all values as strings."""
    # Override default YAML constructors to load all types as strings
    for tag in ("str", "int", "float", "bool", "null", "decimal"):
        yaml.add_constructor(f"tag:yaml.org,2002:{tag}", string_loader)

    yaml.add_constructor("!decimal", string_loader)
    yaml.add_constructor("!isostring", string_loader)
    yaml.add_constructor("!decimallist", list_of_decimal_constructor)

    with open(file_path, "r") as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def format_return_value(case):
    result = case.get("result", {})
    special = result.get("special")

    if special:
        special = special.lower()

        # Handle special cases for ERROR and UNDEFINED
        if special in {"error", "undefined"}:
            return f"<!{special.upper()}>"

        if special == "nan":
            return "nan::fp64"

    # Return formatted result with format_value
    return convert_to_new_value(result.get("value"), result.get("type"))


def format_test_case_group(case, description_map):
    """Extract group name and description for test case."""
    group = case.get("group", "basic")
    group_name = group if isinstance(group, str) else group.get("id", "basic")
    description = group.get("description", "") if isinstance(group, dict) else ""

    if group_name not in description_map:
        description_map[group_name] = description

    return f"{group_name}: {description_map.get(group_name, '')}"


def generate_define_table(case, table_id):
    """Generates the table definition only if there are arguments with 'is_not_a_func_arg'."""
    args = case.get("args", [])

    # If args is empty, return an empty string, as no table is needed
    if not args:
        return ""

    # Gather column types and names based on args
    formatted_columns = ", ".join(str(arg["type"]) for arg in args) if args else ""

    # Transpose the arguments' values to construct rows
    values = [
        [convert_to_new_value(value, arg["type"], 1) for value in arg.get("value", [])]
        for arg in args
    ]
    rows = zip(*values)  # zip will combine each nth element of each argument

    # Format rows as strings for the table definition
    formatted_rows = ", ".join(f"({', '.join(map(str, row))})" for row in rows)

    # Define table format with column types
    table_definition = (
        f"DEFINE t{table_id}({formatted_columns}) = ({formatted_rows}) \n"
    )

    return table_definition


def format_test_case(case, function, description_map, table_id_counter, is_aggregate):
    """Format a single test case."""
    description = format_test_case_group(case, description_map)
    options = case.get("options")
    options = (
        f" [{', '.join(f'{k}:{convert_to_new_value(v, None)}' for k, v in options.items())}]"
        if options
        else ""
    )
    results = format_return_value(case)

    args = [arg for arg in case.get("args", []) if not arg.get("is_not_a_func_arg")]
    if is_aggregate and len(args) != 1:
        table_id = next(table_id_counter)
        args = ", ".join(f"t{table_id}.col{idx}" for idx in range(len(args)))
        table_definition = generate_define_table(case, table_id)
        return description, f"{table_definition}{function}({args}){options} = {results}"

    args = ", ".join(
        convert_to_new_value(arg.get("value"), str(arg["type"]))
        for arg in case.get("args", [])
    )
    return description, f"{function}({args}){options} = {results}"


def convert_test_file_to_new_format(input_data, prefix, is_aggregate):
    """Parse YAML test data to formatted cases."""
    function = input_data["function"]
    base_uri = input_data["base_uri"][len(prefix) :]
    description_map = {}
    table_id_counter = count(0)
    groups = defaultdict(lambda: {"tests": []})

    for case in input_data["cases"]:
        description, formatted_test = format_test_case(
            case, function, description_map, table_id_counter, is_aggregate
        )
        groups[description]["tests"].append(formatted_test)

    output_lines = [
        f"{'### SUBSTRAIT_AGGREGATE_TEST: v1.0' if is_aggregate else '### SUBSTRAIT_SCALAR_TEST: v1.0'}\n",
        f"### SUBSTRAIT_INCLUDE: '{base_uri}'\n",
    ]

    for description, details in groups.items():
        output_lines.append(f"\n# {description}\n")
        output_lines.extend(f"{test}\n" for test in details["tests"])

    return output_lines


def output_test_data(output_file, lines):
    """Write formatted lines to a file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as file:
        file.writelines(lines)

    print(f"Converted '{output_file}' successfully.")


def convert_directory(input_dir, output_dir, prefix):
    """Process all YAML files in a directory, convert and save them to output directory."""
    for root, _, files in os.walk(input_dir):
        for filename in filter(lambda f: f.endswith(".yaml"), files):
            input_file = os.path.join(root, filename)
            output_file = os.path.join(
                output_dir, os.path.relpath(input_file, input_dir)
            ).replace(".yaml", ".test")
            is_aggregate = "aggregate" in input_file

            yaml_data = load_test_file(input_file)
            output_lines = convert_test_file_to_new_format(
                yaml_data, prefix, is_aggregate
            )
            output_test_data(output_file, output_lines)


if __name__ == "__main__":
    input_directory = "./cases"
    output_directory = "./substrait/tests/cases"
    uri_prefix = (
        "https://github.com/substrait-io/substrait/blob/main/extensions/substrait"
    )
    convert_directory(input_directory, output_directory, uri_prefix)
