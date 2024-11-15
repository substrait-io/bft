import pytest

from convert_tests_to_new_format import convert_test_file_to_new_format


@pytest.mark.parametrize(
    "input_data, prefix, is_aggregate, expected_output",
    [
        (
            {
                "base_uri": "https://github.com/substrait-io/substrait/blob/main/extensions/substrait/extensions/functions_arithmetic.yaml",
                "function": "add",
                "cases": [
                    {
                        "group": {
                            "id": "basic",
                            "description": "Basic examples without any special cases",
                        },
                        "args": [
                            {"value": 120, "type": "i8"},
                            {"value": 5, "type": "i8"},
                        ],
                        "result": {"value": 125, "type": "i8"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": 100, "type": "i16"},
                            {"value": 100, "type": "i16"},
                        ],
                        "result": {"value": 200, "type": "i16"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": 30000, "type": "i32"},
                            {"value": 30000, "type": "i32"},
                        ],
                        "result": {"value": 60000, "type": "i32"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": 2000000000, "type": "i64"},
                            {"value": 2000000000, "type": "i64"},
                        ],
                        "result": {"value": 4000000000, "type": "i64"},
                    },
                    {
                        "group": {
                            "id": "overflow",
                            "description": "Examples demonstrating overflow behavior",
                        },
                        "args": [
                            {"value": 120, "type": "i8"},
                            {"value": 10, "type": "i8"},
                        ],
                        "options": {"overflow": "ERROR"},
                        "result": {"special": "error"},
                    },
                    {
                        "group": "overflow",
                        "args": [
                            {"value": 30000, "type": "i16"},
                            {"value": 30000, "type": "i16"},
                        ],
                        "options": {"overflow": "ERROR"},
                        "result": {"special": "error"},
                    },
                    {
                        "group": "overflow",
                        "args": [
                            {"value": 2000000000, "type": "i32"},
                            {"value": 2000000000, "type": "i32"},
                        ],
                        "options": {"overflow": "ERROR"},
                        "result": {"special": "error"},
                    },
                    {
                        "group": "overflow",
                        "args": [
                            {"value": 9223372036854775807, "type": "i64"},
                            {"value": 1, "type": "i64"},
                        ],
                        "options": {"overflow": "ERROR"},
                        "result": {"special": "error"},
                    },
                ],
            },
            "https://github.com/substrait-io/substrait/blob/main/extensions/substrait",
            False,
            [
                "### SUBSTRAIT_SCALAR_TEST: v1.0\n",
                "### SUBSTRAIT_INCLUDE: '/extensions/functions_arithmetic.yaml'\n",
                "\n# basic: Basic examples without any special cases\n",
                "add(120::i8, 5::i8) = 125::i8\n",
                "add(100::i16, 100::i16) = 200::i16\n",
                "add(30000::i32, 30000::i32) = 60000::i32\n",
                "add(2000000000::i64, 2000000000::i64) = 4000000000::i64\n",
                "\n# overflow: Examples demonstrating overflow behavior\n",
                "add(120::i8, 10::i8) [overflow:ERROR] = <!ERROR>\n",
                "add(30000::i16, 30000::i16) [overflow:ERROR] = <!ERROR>\n",
                "add(2000000000::i32, 2000000000::i32) [overflow:ERROR] = <!ERROR>\n",
                "add(9223372036854775807::i64, 1::i64) [overflow:ERROR] = <!ERROR>\n",
            ],
        ),
        # Second test case for "max" function
        (
            {
                "base_uri": "https://github.com/substrait-io/substrait/blob/main/extensions/substrait/extensions/functions_arithmetic.yaml",
                "function": "max",
                "cases": [
                    {
                        "group": {
                            "id": "basic",
                            "description": "Basic examples without any special cases",
                        },
                        "args": [{"value": [20, -3, 1, -10, 0, 5], "type": "i8"}],
                        "result": {"value": 20, "type": "i8"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": [-32768, 32767, 20000, -30000], "type": "i16"}
                        ],
                        "result": {"value": 32767, "type": "i16"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {
                                "value": [-214748648, 214748647, 21470048, 4000000],
                                "type": "i32",
                            }
                        ],
                        "result": {"value": 214748647, "type": "i32"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {
                                "value": [
                                    2000000000,
                                    -3217908979,
                                    629000000,
                                    -100000000,
                                    0,
                                    987654321,
                                ],
                                "type": "i64",
                            }
                        ],
                        "result": {"value": 2000000000, "type": "i64"},
                    },
                    {
                        "group": "basic",
                        "args": [{"value": [2.5, 0, 5.0, -2.5, -7.5], "type": "fp32"}],
                        "result": {"value": 5.0, "type": "fp32"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {
                                "value": [
                                    "1.5e+308",
                                    "1.5e+10",
                                    "-1.5e+8",
                                    "-1.5e+7",
                                    "-1.5e+70",
                                ],
                                "type": "fp64",
                            }
                        ],
                        "result": {"value": "1.5e+308", "type": "fp64"},
                    },
                    {
                        "group": {
                            "id": "null_handling",
                            "description": "Examples with null as input or output",
                        },
                        "args": [{"value": ["Null", "Null", "Null"], "type": "i16"}],
                        "result": {"value": "Null", "type": "i16"},
                    },
                    {
                        "group": "null_handling",
                        "args": [{"value": [], "type": "i16"}],
                        "result": {"value": "Null", "type": "i16"},
                    },
                    {
                        "group": "null_handling",
                        "args": [
                            {
                                "value": [
                                    2000000000,
                                    "Null",
                                    629000000,
                                    -100000000,
                                    "Null",
                                    987654321,
                                ],
                                "type": "i64",
                            }
                        ],
                        "result": {"value": 2000000000, "type": "i64"},
                    },
                    {
                        "group": "null_handling",
                        "args": [{"value": ["Null", "inf"], "type": "fp64"}],
                        "result": {"value": "inf", "type": "fp64"},
                    },
                    {
                        "group": "null_handling",
                        "args": [
                            {
                                "value": [
                                    "Null",
                                    "-inf",
                                    "-1.5e+8",
                                    "-1.5e+7",
                                    "-1.5e+70",
                                ],
                                "type": "fp64",
                            }
                        ],
                        "result": {"value": "-1.5e+7", "type": "fp64"},
                    },
                    {
                        "group": "null_handling",
                        "args": [
                            {
                                "value": [
                                    "1.5e+308",
                                    "1.5e+10",
                                    "Null",
                                    "-1.5e+7",
                                    "Null",
                                ],
                                "type": "fp64",
                            }
                        ],
                        "result": {"value": "1.5e+308", "type": "fp64"},
                    },
                ],
            },
            "https://github.com/substrait-io/substrait/blob/main/extensions/substrait",
            False,
            [
                "### SUBSTRAIT_SCALAR_TEST: v1.0\n",
                "### SUBSTRAIT_INCLUDE: '/extensions/functions_arithmetic.yaml'\n",
                "\n# basic: Basic examples without any special cases\n",
                "max((20, -3, 1, -10, 0, 5)::i8) = 20::i8\n",
                "max((-32768, 32767, 20000, -30000)::i16) = 32767::i16\n",
                "max((-214748648, 214748647, 21470048, 4000000)::i32) = 214748647::i32\n",
                "max((2000000000, -3217908979, 629000000, -100000000, 0, 987654321)::i64) = 2000000000::i64\n",
                "max((2.5, 0, 5.0, -2.5, -7.5)::fp32) = 5.0::fp32\n",
                "max((1.5e+308, 1.5e+10, -1.5e+8, -1.5e+7, -1.5e+70)::fp64) = 1.5e+308::fp64\n",
                "\n# null_handling: Examples with null as input or output\n",
                "max((Null, Null, Null)::i16) = null::i16\n",
                "max(()::i16) = null::i16\n",
                "max((2000000000, Null, 629000000, -100000000, Null, 987654321)::i64) = 2000000000::i64\n",
                "max((Null, inf)::fp64) = inf::fp64\n",
                "max((Null, -inf, -1.5e+8, -1.5e+7, -1.5e+70)::fp64) = -1.5e+7::fp64\n",
                "max((1.5e+308, 1.5e+10, Null, -1.5e+7, Null)::fp64) = 1.5e+308::fp64\n",
            ],
        ),
        # Test case for "lt" function
        (
            {
                "base_uri": "https://github.com/substrait-io/substrait/blob/main/extensions/substrait/extensions/functions_datetime.yaml",
                "function": "lt",
                "cases": [
                    {
                        "group": {
                            "id": "timestamps",
                            "description": "examples using the timestamp type",
                        },
                        "args": [
                            {"value": "2016-12-31 13:30:15", "type": "timestamp"},
                            {"value": "2017-12-31 13:30:15", "type": "timestamp"},
                        ],
                        "result": {"value": True, "type": "boolean"},
                    },
                    {
                        "group": "timestamps",
                        "args": [
                            {"value": "2018-12-31 13:30:15", "type": "timestamp"},
                            {"value": "2017-12-31 13:30:15", "type": "timestamp"},
                        ],
                        "result": {"value": False, "type": "boolean"},
                    },
                    {
                        "group": {
                            "id": "timestamp_tz",
                            "description": "examples using the timestamp_tz type",
                        },
                        "args": [
                            {
                                "value": "1999-01-08 01:05:05 PST",
                                "type": "timestamp_tz",
                            },
                            {
                                "value": "1999-01-08 04:05:06 EST",
                                "type": "timestamp_tz",
                            },
                        ],
                        "result": {"value": True, "type": "boolean"},
                    },
                    {
                        "group": "timestamp_tz",
                        "args": [
                            {
                                "value": "1999-01-08 01:05:06 PST",
                                "type": "timestamp_tz",
                            },
                            {
                                "value": "1999-01-08 04:05:06 EST",
                                "type": "timestamp_tz",
                            },
                        ],
                        "result": {"value": False, "type": "boolean"},
                    },
                    {
                        "group": {
                            "id": "date",
                            "description": "examples using the date type",
                        },
                        "args": [
                            {"value": "2020-12-30", "type": "date"},
                            {"value": "2020-12-31", "type": "date"},
                        ],
                        "result": {"value": True, "type": "boolean"},
                    },
                    {
                        "group": "date",
                        "args": [
                            {"value": "2020-12-31", "type": "date"},
                            {"value": "2020-12-30", "type": "date"},
                        ],
                        "result": {"value": False, "type": "boolean"},
                    },
                    {
                        "group": {
                            "id": "interval",
                            "description": "examples using the interval type",
                        },
                        "args": [
                            {"value": "INTERVAL '5 DAY'", "type": "interval"},
                            {"value": "INTERVAL '6 DAY'", "type": "interval"},
                        ],
                        "result": {"value": True, "type": "boolean"},
                    },
                    {
                        "group": "interval",
                        "args": [
                            {"value": "INTERVAL '7 DAY'", "type": "interval"},
                            {"value": "INTERVAL '6 DAY'", "type": "interval"},
                        ],
                        "result": {"value": False, "type": "boolean"},
                    },
                    {
                        "group": "interval",
                        "args": [
                            {"value": "INTERVAL '5 YEAR'", "type": "interval"},
                            {"value": "INTERVAL '6 YEAR'", "type": "interval"},
                        ],
                        "result": {"value": True, "type": "boolean"},
                    },
                    {
                        "group": "interval",
                        "args": [
                            {"value": "INTERVAL '7 YEAR'", "type": "interval"},
                            {"value": "INTERVAL '6 YEAR'", "type": "interval"},
                        ],
                        "result": {"value": False, "type": "boolean"},
                    },
                    {
                        "group": {
                            "id": "null_input",
                            "description": "examples with null args or return",
                        },
                        "args": [
                            {"value": None, "type": "interval"},
                            {"value": "INTERVAL '5 DAY'", "type": "interval"},
                        ],
                        "result": {"value": None, "type": "boolean"},
                    },
                    {
                        "group": "null_input",
                        "args": [
                            {"value": None, "type": "date"},
                            {"value": "2020-12-30", "type": "date"},
                        ],
                        "result": {"value": None, "type": "boolean"},
                    },
                    {
                        "group": "null_input",
                        "args": [
                            {"value": None, "type": "timestamp"},
                            {"value": "2018-12-31 13:30:15", "type": "timestamp"},
                        ],
                        "result": {"value": None, "type": "boolean"},
                    },
                ],
            },
            "https://github.com/substrait-io/substrait/blob/main/extensions/substrait",
            False,
            [
                "### SUBSTRAIT_SCALAR_TEST: v1.0\n",
                "### SUBSTRAIT_INCLUDE: '/extensions/functions_datetime.yaml'\n",
                "\n# timestamps: examples using the timestamp type\n",
                "lt('2016-12-31T13:30:15'::ts, '2017-12-31T13:30:15'::ts) = true::bool\n",
                "lt('2018-12-31T13:30:15'::ts, '2017-12-31T13:30:15'::ts) = false::bool\n",
                "\n# timestamp_tz: examples using the timestamp_tz type\n",
                "lt('1999-01-08T01:05:05-08:00'::tstz, '1999-01-08T04:05:06-05:00'::tstz) = true::bool\n",
                "lt('1999-01-08T01:05:06-08:00'::tstz, '1999-01-08T04:05:06-05:00'::tstz) = false::bool\n",
                "\n# date: examples using the date type\n",
                "lt('2020-12-30'::date, '2020-12-31'::date) = true::bool\n",
                "lt('2020-12-31'::date, '2020-12-30'::date) = false::bool\n",
                "\n# interval: examples using the interval type\n",
                "lt('P5D'::iday, 'P6D'::iday) = true::bool\n",
                "lt('P7D'::iday, 'P6D'::iday) = false::bool\n",
                "lt('P5Y'::iyear, 'P6Y'::iyear) = true::bool\n",
                "lt('P7Y'::iyear, 'P6Y'::iyear) = false::bool\n",
                "\n# null_input: examples with null args or return\n",
                "lt(null::iday, 'P5D'::iday) = null::bool\n",
                "lt(null::date, '2020-12-30'::date) = null::bool\n",
                "lt(null::ts, '2018-12-31T13:30:15'::ts) = null::bool\n",
            ],
        ),
        (
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
                            {"value": 8, "type": "i64"},
                            {"value": 2, "type": "i64"},
                        ],
                        "result": {"value": 64, "type": "i64"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": 1.0, "type": "fp32"},
                            {"value": -1.0, "type": "fp32"},
                        ],
                        "result": {"value": 1.0, "type": "fp32"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": 2.0, "type": "fp64"},
                            {"value": -2.0, "type": "fp64"},
                        ],
                        "result": {"value": 0.25, "type": "fp64"},
                    },
                    {
                        "group": "basic",
                        "args": [
                            {"value": 13, "type": "i64"},
                            {"value": 10, "type": "i64"},
                        ],
                        "result": {"value": 137858491849, "type": "i64"},
                    },
                    {
                        "group": {
                            "id": "floating_exception",
                            "description": "Examples demonstrating exceptional floating point cases",
                        },
                        "args": [
                            {"value": 1.5e100, "type": "fp64"},
                            {"value": 1.5e208, "type": "fp64"},
                        ],
                        "result": {"value": "inf", "type": "fp64"},
                    },
                ],
            },
            "https://github.com/substrait-io/substrait/blob/main/extensions/substrait",
            False,
            [
                "### SUBSTRAIT_SCALAR_TEST: v1.0\n",
                "### SUBSTRAIT_INCLUDE: '/extensions/functions_arithmetic.yaml'\n",
                "\n# basic: Basic examples without any special cases\n",
                "power(8::i64, 2::i64) = 64::i64\n",
                "power(1.0::fp32, -1.0::fp32) = 1.0::fp32\n",
                "power(2.0::fp64, -2.0::fp64) = 0.25::fp64\n",
                "power(13::i64, 10::i64) = 137858491849::i64\n",
                "\n# floating_exception: Examples demonstrating exceptional floating point cases\n",
                "power(1.5e+100::fp64, 1.5e+208::fp64) = inf::fp64\n",
            ],
        ),
    ],
)
def test_convert_test_file_to_new_format(
    input_data, prefix, is_aggregate, expected_output
):
    result = convert_test_file_to_new_format(input_data, prefix, is_aggregate)
    assert result == expected_output
