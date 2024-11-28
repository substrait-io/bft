from pathlib import Path
from typing import List

import pytest

from bft.cases.parser import CaseFileParser
from bft.cases.types import Case
from bft.testers.base_tester import BaseTester
from tools.convert_testcases.convert_testcases_to_yaml_format import (
    convert_directory as convert_directory_from_substrait,
)


# Would be nice to have this as a session-scoped fixture but it doesn't seem that
# parameter values can be a fixture
def cases() -> List[Case]:
    cases = []
    bft_dir = Path(__file__).parent.parent.parent
    parser = CaseFileParser()
    cases_dir = bft_dir / "cases"
    substrait_cases_dir = bft_dir / "substrait" / "tests" / "cases"
    convert_directory_from_substrait(substrait_cases_dir, cases_dir)
    for case_path in cases_dir.resolve().rglob("*.yaml"):
        with open(case_path, "rb") as case_f:
            for case_file in parser.parse(case_f):
                for case in case_file.cases:
                    case = transform_case(case)
                    cases.append(case)
    return cases


def transform_case(case):
    # Create a new Case instance with updated `args`
    return Case(
        function=case.function,
        base_uri=case.base_uri,
        group=case.group,
        args=case.args,  # Update args here
        result=case.result,
        options=case.options,
    )


def case_id_fn(case: Case):
    return f"{case.function}_{case.group.id}_{case.group.index}"


def run_test(case: Case, tester: BaseTester):
    if tester.runner.__class__.__name__ == "VeloxRunner":
        for case_literal in case.args:
            if case_literal.value is None:
                pytest.skip("Skipping. Pyvelox does not support null input")
    if tester.runner.__class__.__name__ == "PostgresRunner":
        if type(case.result) != str and "inf" in str(case.result[0]):
            pytest.skip(
                "Skipping. Postgres errors out when dealing with infinite addition"
            )
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
