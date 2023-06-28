import json
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent
JSON_DIR = BASE_DIR / "function_json"
CASES_DIR = BASE_DIR / "cases"
FUNCTION_FOLDERS = Path(CASES_DIR).glob("*")


for function_folder in FUNCTION_FOLDERS:
    folder_path = CASES_DIR / function_folder.name
    json_path = JSON_DIR / function_folder.name
    Path(json_path).mkdir(parents=True, exist_ok=True)
    function_yamls = Path(folder_path).rglob("*.yaml")
    for function_yaml in function_yamls:
        yaml_file = folder_path / function_yaml.name
        json_file = json_path / function_yaml.stem
        with open(yaml_file) as f:
            dataMap = yaml.safe_load(f)
            with open(f"{json_file}.json", "w") as outfile:
                outfile.write('{}\n'.format(json.dumps(dataMap, indent=4)))
