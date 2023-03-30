from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, NamedTuple

from bft.cases.runner import CaseRunner
from bft.cases.types import Case
from bft.dialects.types import Dialect, DialectsLibrary


class TestResult(NamedTuple):
    function: str
    group: str
    index: int
    passed: bool
    should_have_passed: bool
    reason: str


class BaseTester(ABC):
    @abstractmethod
    def get_runner(self, dialect: Dialect) -> CaseRunner:
        pass

    @abstractmethod
    def get_dialect(self, library: DialectsLibrary) -> Dialect:
        pass

    def prepare(self, dialects: DialectsLibrary):
        self.dialect = self.get_dialect(dialects)
        self.runner = self.get_runner(self.dialect)
        self.group_indices = {}

    def run_test(self, case: Case) -> TestResult:
        result = self.runner.run_case(case)
        group_index = self.group_indices.get(case.group.id, 0)
        self.group_indices[case.group.id] = group_index + 1
        return TestResult(
            case.function,
            case.group.id,
            group_index,
            result.passed,
            result.expected_pass,
            result.reason,
        )
