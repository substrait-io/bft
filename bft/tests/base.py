from pathlib import Path
from typing import List

import pytest

from bft.cases.parser import CaseFileParser
from bft.cases.types import Case
from bft.dialects.types import DialectsLibrary
from bft.testers.base_tester import BaseTester


# Would be nice to have this as a session-scoped fixture but it doesn't seem that
# parameter values can be a fixture
def cases() -> List[Case]:
    cases = []
    parser = CaseFileParser()
    cases_dir = Path(__file__) / ".." / ".." / ".." / "cases"
    for case_path in cases_dir.resolve().rglob("*.yaml"):
        with open(case_path, "rb") as case_f:
            for case_file in parser.parse(case_f):
                for case in case_file.cases:
                    cases.append(case)
    return cases

def case_id_fn(case: Case):
    return f"{case.function}_{case.group.id}_{case.group.index}"

def run_test(case: Case, tester: BaseTester):
    result = tester.run_test(case)
    if result.passed:
        if not result.should_have_passed:
            pytest.fail(f"Unexpected pass: {result.reason}")
        else:
            assert result.passed
    else:
        if result.should_have_passed:
            pytest.fail(f"Unexpected fail: {result.reason}")
        else:
            pytest.xfail(result.reason)
