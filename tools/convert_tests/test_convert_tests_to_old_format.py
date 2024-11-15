import pytest

from convert_tests_to_old_format import convert_test_file_to_yaml
from tests.coverage.nodes import (
    TestFile,
    TestCase,
    CaseLiteral,
    CaseGroup,
)


@pytest.mark.parametrize(
    "test_file, expected_yaml",
    [
        (
            TestFile(
                path="test_path",
                version="v1.0",
                include="/extensions/functions_arithmetic.yaml",
                testcases=[
                    TestCase(
                        func_name="power",
                        base_uri="https://github.com/substrait-io/substrait",
                        group=CaseGroup(
                            name="basic: Basic examples without any special cases",
                            description="",
                        ),
                        options={},
                        rows=None,
                        args=[
                            CaseLiteral(value=8, type="i64"),
                            CaseLiteral(value=2, type="i64"),
                        ],
                        result=CaseLiteral(value=64, type="i64"),
                        comment="",
                    ),
                    TestCase(
                        func_name="power",
                        base_uri="https://github.com/substrait-io/substrait",
                        group=CaseGroup(
                            name="basic: Basic examples without any special cases",
                            description="",
                        ),
                        options={},
                        rows=None,
                        args=[
                            CaseLiteral(value=1.0, type="fp32"),
                            CaseLiteral(value=-1.0, type="fp32"),
                        ],
                        result=CaseLiteral(value=1.0, type="fp32"),
                        comment="",
                    ),
                    TestCase(
                        func_name="power",
                        base_uri="https://github.com/substrait-io/substrait",
                        group=CaseGroup(
                            name="basic: Basic examples without any special cases",
                            description="",
                        ),
                        options={},
                        rows=None,
                        args=[
                            CaseLiteral(value=2.0, type="fp64"),
                            CaseLiteral(value=-2.0, type="fp64"),
                        ],
                        result=CaseLiteral(value=0.25, type="fp64"),
                        comment="",
                    ),
                    TestCase(
                        func_name="power",
                        base_uri="https://github.com/substrait-io/substrait",
                        group=CaseGroup(
                            name="basic: Basic examples without any special cases",
                            description="",
                        ),
                        options={},
                        rows=None,
                        args=[
                            CaseLiteral(value=13, type="i64"),
                            CaseLiteral(value=10, type="i64"),
                        ],
                        result=CaseLiteral(value=137858491849, type="i64"),
                        comment="",
                    ),
                    TestCase(
                        func_name="power",
                        base_uri="https://github.com/substrait-io/substrait",
                        group=CaseGroup(
                            name="floating_exception: Examples demonstrating exceptional floating point cases",
                            description="",
                        ),
                        options={},
                        rows=None,
                        args=[
                            CaseLiteral(value=1.5e100, type="fp64"),
                            CaseLiteral(value=1.5e208, type="fp64"),
                        ],
                        result=CaseLiteral(value="inf", type="fp64"),
                        comment="",
                    ),
                ],
            ),
            {
                "base_uri": "https://github.com/substrait-io/substrait/blob/main/extensions/substrait/extensions/functions_arithmetic.yaml",
                "function": "power",
                "cases": [
                    {
                        "group": {
                            "id": "basic",
                            "description": "Basic examples without any special cases",
                        },
                        "args": [
                            {"value": "8", "type": "i64"},
                            {"value": "2", "type": "i64"},
                        ],
                        "result": {"value": "64", "type": "i64"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": "1.0", "type": "fp32"},
                            {"value": "-1.0", "type": "fp32"},
                        ],
                        "result": {"value": "1.0", "type": "fp32"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": "2.0", "type": "fp64"},
                            {"value": "-2.0", "type": "fp64"},
                        ],
                        "result": {"value": "0.25", "type": "fp64"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": "13", "type": "i64"},
                            {"value": "10", "type": "i64"},
                        ],
                        "result": {"value": "137858491849", "type": "i64"},
                    },
                    {
                        "group": {
                            "id": "floating_exception",
                            "description": "Examples demonstrating exceptional floating point cases",
                        },
                        "args": [
                            {"value": "1.5e+100", "type": "fp64"},
                            {"value": "1.5e+208", "type": "fp64"},
                        ],
                        "result": {"value": "inf", "type": "fp64"},
                    },
                ],
            },
        ),
        (
            TestFile(
                path="test_path",
                version="v1.0",
                include="/extensions/functions_arithmetic.yaml",
                testcases=[
                    TestCase(
                        func_name="max",
                        base_uri="https://github.com/substrait-io/substrait",
                        group=CaseGroup(
                            name="basic: Basic examples without any special cases",
                            description="",
                        ),
                        options={},
                        rows=None,
                        args=[
                            CaseLiteral(value=20, type="i8"),
                            CaseLiteral(value=-3, type="i8"),
                            CaseLiteral(value=1, type="i8"),
                            CaseLiteral(value=-10, type="i8"),
                            CaseLiteral(value=0, type="i8"),
                            CaseLiteral(value=5, type="i8"),
                        ],
                        result=CaseLiteral(value=20, type="i8"),
                        comment="",
                    ),
                    TestCase(
                        func_name="max",
                        base_uri="https://github.com/substrait-io/substrait",
                        group=CaseGroup(
                            name="basic: Basic examples without any special cases",
                            description="",
                        ),
                        options={},
                        rows=None,
                        args=[
                            CaseLiteral(value=-32768, type="i16"),
                            CaseLiteral(value=32767, type="i16"),
                            CaseLiteral(value=20000, type="i16"),
                            CaseLiteral(value=-30000, type="i16"),
                        ],
                        result=CaseLiteral(value=32767, type="i16"),
                        comment="",
                    ),
                ],
            ),
            {
                "base_uri": "https://github.com/substrait-io/substrait/blob/main/extensions/substrait/extensions/functions_arithmetic.yaml",
                "function": "max",
                "cases": [
                    {
                        "group": {
                            "id": "basic",
                            "description": "Basic examples without any special cases",
                        },
                        "args": [
                            {"value": "20", "type": "i8"},
                            {"value": "-3", "type": "i8"},
                            {"value": "1", "type": "i8"},
                            {"value": "-10", "type": "i8"},
                            {"value": "0", "type": "i8"},
                            {"value": "5", "type": "i8"},
                        ],
                        "result": {"value": "20", "type": "i8"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": "-32768", "type": "i16"},
                            {"value": "32767", "type": "i16"},
                            {"value": "20000", "type": "i16"},
                            {"value": "-30000", "type": "i16"},
                        ],
                        "result": {"value": "32767", "type": "i16"},
                    },
                ],
            },
        ),
    ],
)
def test_convert_test_file_to_yaml(test_file, expected_yaml):
    result = convert_test_file_to_yaml(test_file)
    assert result == expected_yaml
