from abc import ABC, abstractmethod
from typing import Literal, NamedTuple

from bft.dialects.types import Dialect, SqlMapping

from .types import Case


class CaseResult(NamedTuple):
    passed: bool
    expected_pass: bool
    reason: str


class CaseRunner(ABC):
    @abstractmethod
    def run_case(self, case: Case) -> CaseResult:
        pass


class SqlCaseResult(NamedTuple):
    type: Literal["success", "error", "unsupported", "unexpected_pass", "mismatch"]
    err: str
    actual: str

    @staticmethod
    def success():
        return SqlCaseResult("success", None, None)

    @staticmethod
    def error(err: str):
        return SqlCaseResult("error", err, None)

    @staticmethod
    def unsupported(err: str):
        return SqlCaseResult("unsupported", err, None)

    @staticmethod
    def unexpected_pass(actual: str):
        return SqlCaseResult("unexpected_pass", None, actual)

    @staticmethod
    def mismatch(actual: str):
        return SqlCaseResult("mismatch", None, actual)


class SqlCaseRunner(CaseRunner):
    def __init__(self, dialect: Dialect):
        self.__dialect = dialect

    def run_case(self, case: Case) -> CaseResult:
        mapping = self.__dialect.mapping_for_case(case)
        if mapping is None:
            return CaseResult(
                False,
                False,
                f"The dialect {self.__dialect.name} does not support the function '{case.function}'",
            )
        result = self.run_sql_case(case, mapping)
        if result.type == "success":
            return CaseResult(result, mapping.should_pass, mapping.reason)
        elif result.type == "unsupported":
            if mapping.should_pass:
                return CaseResult(
                    False,
                    True,
                    f"This case should have been supported.  Instead it reported {result.err}",
                )
            else:
                return CaseResult(False, False, mapping.reason)
        elif result.type == "error":
            if case.result == "error":
                # Case expected to error.  Dialect may or may not have expected it
                return CaseResult(True, mapping.should_pass, mapping.reason)
            else:
                if mapping.should_pass:
                    # Case should not have error.  Dialect should not have error
                    return CaseResult(False, mapping.should_pass, result.err)
                else:
                    # Case should not have error but it's expected for dialect
                    return CaseResult(False, mapping.should_pass, mapping.reason)
        elif result.type == "unexpected_pass":
            # Case expected error.  No error happened.
            if mapping.should_pass:
                # This was not expected given the dialect
                return CaseResult(
                    False,
                    mapping.should_pass,
                    f"This case should have given an error.  Instead it returned the value {result.actual}",
                )
            else:
                # In this dialect, this case passes even though it shouldn't
                return CaseResult(False, mapping.should_pass, mapping.reason)
        elif result.type == "mismatch":
            if mapping.should_pass:
                return CaseResult(
                    False,
                    mapping.should_pass,
                    f"This case should have yielded the result {case.result.value} but instead it returned {result.actual}",
                )
            else:
                return CaseResult(False, mapping.should_pass, mapping.reason)
        else:
            raise Exception("Unexpected case result type")

    @abstractmethod
    def run_sql_case(self, case: Case, mapping: SqlMapping) -> SqlCaseResult:
        pass
