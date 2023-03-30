from pathlib import Path
from typing import List

from .parser import CaseFileParser
from .types import Case


def load_cases(cases_dir: str) -> List[Case]:
    cases = []
    parser = CaseFileParser()
    for case_path in Path(cases_dir).rglob("*.yaml"):
        with open(case_path, "rb") as case_f:
            for case_file in parser.parse(case_f):
                for case in case_file.cases:
                    cases.append(case)
    return cases