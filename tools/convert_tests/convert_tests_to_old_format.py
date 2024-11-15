import os

from ruamel.yaml import YAML
from tests.coverage.nodes import (
    TestFile,
    AggregateArgument,
)
from tests.coverage.case_file_parser import load_all_testcases
from tools.convert_tests.convert_tests_helper import (
    convert_to_old_value,
    convert_to_long_type,
    SQUOTE,
    DQUOTE,
    iso_duration_to_timedelta,
)

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)  # Adjust indentations as needed
yaml.width = 4096  # Extend line width to prevent line breaks


def convert_result(test_case):
    """Convert the result section based on specific conditions."""
    if test_case.is_return_type_error():
        return {"special": str(test_case.result.error)}
    elif str(test_case.result.value) == "nan":
        return {"special": "nan"}
    elif test_case.func_name == "add_intervals" and test_case.result.type == "iday":
        return {
            "value": convert_to_old_value(
                iso_duration_to_timedelta(test_case.result.value), "str"
            ),
            "type": "string",
        }
    else:
        return {
            "value": convert_to_old_value(
                test_case.result.value, test_case.result.type
            ),
            "type": convert_to_long_type(test_case.result.type),
        }


def convert_table_definition(test_case):
    column_types = None

    if test_case.column_types is not None:
        column_types = [convert_to_long_type(type) for type in test_case.column_types]
    elif test_case.args is not None:
        column_types = [
            convert_to_long_type(
                arg.scalar_value.type
                if isinstance(arg, AggregateArgument)
                else arg.type
            )
            for arg in test_case.args
        ]

    columns = list(map(list, zip(*test_case.rows)))
    if not columns:
        # Handle the case where columns is empty, but column_types is not
        return [
            {"value": [], "type": col_type, "is_not_a_func_arg": "true"}
            for col_type in column_types
        ]
    else:
        # Handle the case where columns is not empty
        return [
            {
                "value": convert_to_old_value(column, col_type),
                "type": col_type,
                "is_not_a_func_arg": "true",
            }
            for column, col_type in zip(columns, column_types)
        ]


def convert_group(test_case, groups):
    id = str(test_case.group.name.split(": ")[0])
    desc = test_case.group.name.split(": ")[1] if ": " in test_case.group.name else ""
    group = id if id in groups else {"id": id, "description": desc}
    groups[id] = desc
    return group


def convert_test_case_to_old_format(test_case, groups):
    # Match group headers with descriptions
    print(f"converting test '{test_case}'")
    case = {}
    case["group"] = convert_group(test_case, groups)

    if test_case.rows is not None:
        case["args"] = convert_table_definition(test_case)
    else:
        if isinstance(test_case.args[0], AggregateArgument):
            case["args"] = [
                {
                    "value": convert_to_old_value(
                        arg.scalar_value.value, arg.scalar_value.type
                    ),
                    "type": convert_to_long_type(arg.scalar_value.type),
                }
                for arg in test_case.args
            ]
        else:
            case["args"] = [
                {
                    "value": convert_to_old_value(arg.value, arg.type),
                    "type": convert_to_long_type(arg.type),
                }
                for arg in test_case.args
            ]

    if len(test_case.options) > 0:
        case["options"] = {
            key: convert_to_old_value(value, None)
            for key, value in test_case.options.items()
        }

    case["result"] = convert_result(test_case)
    return case


def convert_test_file_to_yaml(testFile: TestFile):
    # Get function name from the first expression
    function = None
    cases = []
    groups = {}

    for test_case in testFile.testcases:
        function = test_case.func_name
        cases.append(convert_test_case_to_old_format(test_case, groups))

    # Construct the full YAML structure
    return {
        "base_uri": f"https://github.com/substrait-io/substrait/blob/main/extensions/substrait{testFile.include}",
        "function": function,
        "cases": cases,
    }


def output_test_data(output_file, input_path, yaml_data):
    with open(output_file, "w") as f:
        yaml.dump(yaml_data, f)

    fix_quotes(output_file)

    print(f"Converted '{input_path}' to '{output_file}'.")


def fix_quotes(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    # Remove all single quotes
    content = (
        content.replace("'", "")
        .replace('"', "")
        .replace(SQUOTE, "'")
        .replace(DQUOTE, '"')
    )

    with open(file_path, "w") as file:
        file.write(content)


def convert_directory(input_dir, output_dir):
    input_test_files = load_all_testcases(input_dir)
    for input_test_file in input_test_files:
        input_file = input_test_file.path
        relative_path = os.path.relpath(input_file, input_dir)
        output_file = os.path.join(output_dir, relative_path).replace(".test", ".yaml")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        yaml_data = convert_test_file_to_yaml(input_test_file)
        output_test_data(output_file, input_test_file.path, yaml_data)


def main():
    input_dir = "../../substrait/tests/cases"
    output_dir = "../../cases"  # Specify the output directory
    convert_directory(input_dir, output_dir)


if __name__ == "__main__":
    main()

from io import StringIO


def normalize_yaml(yaml_string):
    """Normalize YAML by loading it into Python objects and then dumping it back to a string."""
    # If the input is a dictionary or list, convert it to a YAML string first
    yaml_stream = StringIO(yaml_string)

    # Load the YAML from the string (as a stream)
    return yaml.load(yaml_stream)
