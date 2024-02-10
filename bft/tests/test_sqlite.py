import pytest

from bft.testers.sqlite.tester import SqliteTester

from .base import cases, run_test


@pytest.fixture(scope="module")
def tester(dialects):
    instance = SqliteTester()
    instance.prepare(dialects)
    return instance


@pytest.mark.parametrize("case", cases())
def test_functions(case, tester):
    run_test(case, tester)
