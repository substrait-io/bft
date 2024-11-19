import os
import re
import shutil

from ruamel.yaml import YAML
from deepdiff import DeepDiff

from convert_testcases_to_substrait_test_format import (
    convert_directory as convert_directory_to_substrait,
    load_test_file,
)
from convert_testcases_to_yaml_format import (
    convert_directory as convert_directory_to_yaml,
)


def compare_test_files(original_file, roundtrip_file):
    o_file = load_test_file(original_file)
    r_file = load_test_file(roundtrip_file)
    assert o_file == r_file


# Compare tests in yaml format, roundtrip_dir contains files converted from substrait test format to yaml
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

                if not compare_test_files(original_file, roundtrip_file):
                    count += 1
                else:
                    print(f"YAML content matches: {original_file} and {roundtrip_file}")
    return count


def main():
    # Directories
    initial_cases_dir = "../../substrait/tests/cases"
    temp_dir = "./temp"
    intermediate_dir = f"{temp_dir}/bft_cases"
    roundtrip_dir = f"{temp_dir}/roundtrip_substrait_cases"
    uri_prefix = (
        "https://github.com/substrait-io/substrait/blob/main/extensions/substrait"
    )

    # Step 1: Convert from initial_cases_dir to intermediate_dir
    convert_directory_to_yaml(initial_cases_dir, intermediate_dir)

    # Step 2: Convert from intermediate_dir to roundtrip_dir
    convert_directory_to_substrait(intermediate_dir, roundtrip_dir, uri_prefix)

    # Step 3: Compare tests in initial and rounttrip_dir in yaml format
    count = compare_directories(initial_cases_dir, roundtrip_dir)
    if count == 0:
        print(
            "All substrait test files match between original and roundtrip directories."
        )
    else:
        print(
            f"Differences found in {count} test files between original and roundtrip directories."
        )

    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
