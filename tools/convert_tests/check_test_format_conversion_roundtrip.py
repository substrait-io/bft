import os
import re
import shutil

from ruamel.yaml import YAML
from deepdiff import DeepDiff

from convert_tests_to_new_format import convert_directory, load_test_file
from convert_tests_to_old_format import convert_directory as convert_directory_roundtrip

# Initialize the YAML handler with ruamel to ensure consistency in parsing and dumping
yaml = YAML()
yaml.default_flow_style = None


def normalize_data(data):
    """Normalize the data by removing spaces around values and quotes around strings."""
    if isinstance(data, dict):
        return {k: normalize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_data(item) for item in data]
    elif isinstance(data, str):
        # Remove extra spaces in specific cases, like decimal<38,0> vs decimal<38, 0>
        data = re.sub(r"\s*,\s*", ",", data)  # Remove spaces around commas
        if data.lower() == "null":
            return "null"
        return data
    else:
        return data  # Return non-string values as the


def compare_yaml_files(file1, file2):
    data1 = normalize_data(load_test_file(file1))
    data2 = normalize_data(load_test_file(file2))

    diff = DeepDiff(
        data1, data2, ignore_order=True, ignore_numeric_type_changes=True, view="text"
    )
    if diff:
        print(f"\nDifferences found in '{file1}' vs '{file2}':")
        print(diff)
    return not diff


def compare_directories(original_dir, roundtrip_dir):
    count = 0
    for root, _, files in os.walk(original_dir):
        for file_name in files:
            if file_name.endswith(".yaml"):
                original_file = os.path.join(root, file_name)
                relative_path = os.path.relpath(original_file, original_dir)
                roundtrip_file = os.path.join(roundtrip_dir, relative_path).replace(
                    ".test", ".yaml"
                )

                if not os.path.exists(roundtrip_file):
                    print(f"File missing in roundtrip directory: {roundtrip_file}")
                    count += 1
                    continue

                if not compare_yaml_files(original_file, roundtrip_file):
                    count += 1
                else:
                    print(f"YAML content matches: {original_file} and {roundtrip_file}")
    return count


def main():
    # Directories
    initial_cases_dir = "../../cases"
    temp_dir = "./temp"
    intermediate_dir = f"{temp_dir}/substrait_cases"
    roundtrip_dir = f"{temp_dir}/cases"
    uri_prefix = (
        "https://github.com/substrait-io/substrait/blob/main/extensions/substrait"
    )

    # Step 1: Convert from `../../cases` to `./temp/substrait_cases/`
    convert_directory(initial_cases_dir, intermediate_dir, uri_prefix)

    # Step 2: Convert from `./temp/substrait_cases/` to `./temp/roundtrip_cases/`
    convert_directory_roundtrip(intermediate_dir, roundtrip_dir)

    # Step 3: Compare YAML content in `./cases` and `./temp/roundtrip_cases/`
    count = compare_directories(initial_cases_dir, roundtrip_dir)
    if count == 0:
        print("All YAML files match between original and roundtrip directories.")
    else:
        print(
            f"Differences found in {count} YAML files between original and roundtrip directories."
        )

    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
