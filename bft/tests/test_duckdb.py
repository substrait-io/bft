import pytest

from bft.testers.duckdb.tester import DuckDBTester

from .base import cases, run_test


@pytest.fixture(scope="module")
def tester(dialects):
    instance = DuckDBTester()
    instance.prepare(dialects)
    return instance


@pytest.mark.parametrize("case", cases())
def test_scalar_functions(case, tester):
    run_test(case, tester)
