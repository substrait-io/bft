import pytest

from bft.testers.postgres.tester import PostgresTester

from .base import cases, run_test


@pytest.fixture(scope="module")
def tester(dialects):
    instance = PostgresTester()
    instance.prepare(dialects)
    return instance


@pytest.mark.parametrize("case", cases())
def test_functions(case, tester):
    run_test(case, tester)
