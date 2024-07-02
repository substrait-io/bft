import pytest

from bft.testers.snowflake.tester import SnowflakeTester

from .base import cases, run_test


@pytest.fixture(scope="module")
def tester(dialects):
    instance = SnowflakeTester()
    instance.prepare(dialects)
    return instance


@pytest.mark.parametrize("case", cases())
def test_functions(case, tester):
    run_test(case, tester)
