# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import itertools
from collections import OrderedDict, namedtuple
from decimal import Decimal

import pytablewriter as ptw
import pytest
import six
from six.moves import zip
from tabledata import InvalidDataError, PatternMatch, TableData


attr_list_2 = ["attr_a", "attr_b"]

NamedTuple2 = namedtuple("NamedTuple2", " ".join(attr_list_2))


class Test_TableData_constructor(object):
    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [
            [
                "normal",
                ["a", "b"],
                [[1, 2], [3, 4]],
                TableData("normal", ["a", "b"], [[1, 2], [3, 4]]),
            ],
            ["empty_records", ["a", "b"], [], TableData("empty_records", ["a", "b"], [])],
            ["empty_header", [], [[1, 2], [3, 4]], TableData("empty_header", [], [[1, 2], [3, 4]])],
        ],
    )
    def test_normal(self, table_name, header_list, record_list, expected):
        tabledata = TableData(table_name, header_list, record_list)

        print("expected: {}".format(ptw.dump_tabledata(expected)))
        print("actual: {}".format(ptw.dump_tabledata(tabledata)))

        assert tabledata == expected

    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [
            [
                "none_header",
                None,
                [[1, 2], [3, 4]],
                TableData("none_header", None, [[1, 2], [3, 4]]),
            ],
            ["none_records", ["a", "b"], None, TableData("none_records", ["a", "b"], [])],
            ["none_data", None, None, TableData("none_data", [], [])],
        ],
    )
    def test_normal_with_none_value(self, table_name, header_list, record_list, expected):
        tabledata = TableData(table_name, header_list, record_list)

        assert tabledata == expected

    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [["invalid_data", ["a", "b"], [1, 2], InvalidDataError]],
    )
    def test_exception(self, table_name, header_list, record_list, expected):
        with pytest.raises(expected):
            TableData(table_name, header_list, record_list).value_matrix


def yield_rows():
    row_list = [[1, 2], [3, 4]]

    for row in row_list:
        yield row


class Test_TableData_num_rows(object):
    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [
            ["normal", ["a", "b"], [[1, 2], [3, 4]], 2],
            ["empty", ["a", "b"], [], 0],
            ["zip", ["a", "b"], zip(["a", 1], ["b", 2]), None],
            ["empty", ["a", "b"], yield_rows(), None],
            ["empty", ["a", "b"], itertools.product([[1, 2], [3, 4]]), None],
        ],
    )
    def test_normal(self, table_name, header_list, record_list, expected):
        table_data = TableData(table_name, header_list, record_list)

        assert table_data.num_columns == 2
        assert table_data.num_rows == expected


class Test_TableData_eq(object):

    __DATA_0 = TableData(
        "Sheet1",
        ["i", "f", "c", "if", "ifc", "bool", "inf", "nan", "mix_num", "time"],
        [
            [1, "1.1", "aa", 1, 1, "True", float("inf"), "nan", 1, "2017-01-01T00:00:00"],
            [
                2,
                "2.2",
                "bbb",
                "2.2",
                "2.2",
                "False",
                float("inf"),
                float("NaN"),
                float("inf"),
                "2017-01-02 03:04:05+09:00",
            ],
            [
                3,
                "3.33",
                "cccc",
                -3,
                "ccc",
                "True",
                float("inf"),
                float("NaN"),
                float("NaN"),
                "2017-01-01T00:00:00",
            ],
        ],
    )
    __DATA_10 = TableData("tablename", ["a", "b"], [])
    __DATA_11 = TableData("tablename", ["a", "b"], [[1, 2], [11, 12]])

    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [[__DATA_0, __DATA_0, True], [__DATA_0, __DATA_10, False], [__DATA_10, __DATA_11, False]],
    )
    def test_normal(self, lhs, rhs, expected):
        assert (lhs == rhs) == expected
        assert (lhs != rhs) == (not expected)


class Test_TableData_equals(object):

    __LHS = TableData("tablename", ["a", "b"], [{"a": 1, "b": 2}, {"a": 11, "b": 12}])
    __RHS = TableData("tablename", ["a", "b"], [[1, 2], [11, 12]])

    @pytest.mark.parametrize(
        ["lhs", "rhs", "is_strict", "expected"],
        [[__LHS, __RHS, False, True], [__LHS, __RHS, True, False]],
    )
    def test_normal(self, lhs, rhs, is_strict, expected):
        assert lhs.equals(rhs, is_strict=is_strict) == expected
        assert lhs.in_tabledata_list([rhs], is_strict=is_strict) == expected
        assert lhs.in_tabledata_list([lhs], is_strict=is_strict)
        assert lhs.in_tabledata_list([rhs, lhs], is_strict=is_strict)


class Test_TableData_repr(object):
    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [
            [
                "normal",
                ["a", "b"],
                [[1, 2], [3, 4]],
                "table_name=normal, header_list=[a, b], rows=2",
            ],
            [
                "null_header",
                None,
                [[1, 2], [3, 4]],
                "table_name=null_header, header_list=[], rows=2",
            ],
            ["null_header", [], [[1, 2], [3, 4]], "table_name=null_header, header_list=[], rows=2"],
            ["null_body", ["a", "b"], [], "table_name=null_body, header_list=[a, b], rows=0"],
            ["マルチバイト", ["いろは", "漢字"], [], "table_name=マルチバイト, header_list=[いろは, 漢字], rows=0"],
        ],
    )
    def test_normal(self, table_name, header_list, record_list, expected):
        tabledata = TableData(table_name, header_list, record_list)

        assert six.text_type(tabledata) == expected


class Test_TableData_as_dict(object):
    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [
            [
                "normal",
                ["a", "b"],
                [[1, 2], [3, 4]],
                {"normal": [OrderedDict([("a", 1), ("b", 2)]), OrderedDict([("a", 3), ("b", 4)])]},
            ],
            [
                "number",
                ["a", "b"],
                [[1, 2.0], [3.3, Decimal("4.4")]],
                {
                    "number": [
                        OrderedDict([("a", 1), ("b", 2)]),
                        OrderedDict([("a", Decimal("3.3")), ("b", Decimal("4.4"))]),
                    ]
                },
            ],
            [
                "include_none",
                ["a", "b"],
                [[None, 2], [None, None], [3, None], [None, None]],
                {"include_none": [OrderedDict([("b", 2)]), OrderedDict([("a", 3)])]},
            ],
            ["empty_records", ["a", "b"], [], {"empty_records": []}],
        ],
    )
    def test_normal(self, table_name, header_list, record_list, expected):
        assert TableData(table_name, header_list, record_list).as_dict() == expected


class Test_TableData_value_dp_matrix(object):

    __MIXED_DATA = [
        [1, 2],
        (3, 4),
        {"attr_a": 5, "attr_b": 6},
        {"attr_a": 7, "attr_b": 8, "not_exist_attr": 100},
        {"attr_a": 9},
        {"attr_b": 10},
        {},
        NamedTuple2(11, None),
    ]

    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [
            [
                "mixdata",
                attr_list_2,
                __MIXED_DATA,
                TableData(
                    "mixdata",
                    attr_list_2,
                    [
                        [1, 2],
                        [3, 4],
                        [5, 6],
                        [7, 8],
                        [9, None],
                        [None, 10],
                        [None, None],
                        [11, None],
                    ],
                ),
            ],
            [
                "none_header",
                None,
                [[1, 2], [3, 4]],
                TableData("none_header", None, [[1, 2], [3, 4]]),
            ],
            ["none_records", ["a", "b"], None, TableData("none_records", ["a", "b"], [])],
            ["none_data", None, None, TableData("none_data", [], [])],
        ],
    )
    def test_normal(self, table_name, header_list, record_list, expected):
        tabledata = TableData(table_name, header_list, record_list)

        assert not tabledata.has_value_dp_matrix
        assert tabledata.value_dp_matrix == expected.value_dp_matrix
        assert tabledata.has_value_dp_matrix


class Test_TableData_is_empty_header(object):
    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [["tablename", [], [], True], ["tablename", ["a", "b"], [], False]],
    )
    def test_normal(self, table_name, header_list, record_list, expected):
        tabledata = TableData(table_name, header_list, record_list)

        assert tabledata.is_empty_header() == expected


class Test_TableData_is_empty_rows(object):
    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [
            ["tablename", [], [], True],
            ["tablename", ["a", "b"], [], True],
            ["tablename", ["a", "b"], [[1, 2]], False],
        ],
    )
    def test_normal(self, table_name, header_list, record_list, expected):
        tabledata = TableData(table_name, header_list, record_list)

        assert tabledata.is_empty_rows() == expected


class Test_TableData_is_empty(object):
    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [
            ["tablename", [], [], True],
            ["tablename", ["a", "b"], [], True],
            ["tablename", ["a", "b"], [[1, 2]], False],
        ],
    )
    def test_normal(self, table_name, header_list, record_list, expected):
        tabledata = TableData(table_name, header_list, record_list)

        assert tabledata.is_empty() == expected


class Test_TableData_validate_rows(object):
    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list"],
        [["tablename", [], []], ["tablename", ["a", "b"], []], ["tablename", ["a", "b"], [[1, 2]]]],
    )
    def test_normal(self, table_name, header_list, record_list):
        TableData(table_name, header_list, record_list).validate_rows()

    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "expected"],
        [
            ["tablename", ["a", "b"], [[1]], ValueError],
            ["tablename", ["a", "b"], [[1, 2, 3]], ValueError],
        ],
    )
    def test_exception(self, table_name, header_list, record_list, expected):
        with pytest.raises(expected):
            TableData(table_name, header_list, record_list).validate_rows()


class Test_TableData_filter_column(object):
    HEADER_LIST = ["abcde", "test"]
    VALUE_MATRIX = [[1, 2], [3, 4]]

    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "pattern", "is_invert_match", "expected"],
        [
            [
                "match",
                HEADER_LIST,
                VALUE_MATRIX,
                ["abcde"],
                False,
                TableData("match", ["abcde"], [[1], [3]]),
            ],
            [
                "multiple_match",
                HEADER_LIST,
                VALUE_MATRIX,
                ["abcde", "test"],
                False,
                TableData("multiple_match", ["abcde", "test"], [[1, 2], [3, 4]]),
            ],
            [
                "invert_match",
                HEADER_LIST,
                VALUE_MATRIX,
                ["abcde"],
                True,
                TableData("invert_match", ["test"], [[2], [4]]),
            ],
            [
                "none",
                HEADER_LIST,
                VALUE_MATRIX,
                None,
                False,
                TableData("none", HEADER_LIST, VALUE_MATRIX),
            ],
            [
                "empty",
                HEADER_LIST,
                VALUE_MATRIX,
                [],
                False,
                TableData("empty", HEADER_LIST, VALUE_MATRIX),
            ],
        ],
    )
    def test_normal_match(
        self, table_name, header_list, record_list, pattern, is_invert_match, expected
    ):
        tabledata = TableData(table_name, header_list, record_list)
        actual = tabledata.filter_column(pattern_list=pattern, is_invert_match=is_invert_match)

        print("expected: {}".format(ptw.dump_tabledata(expected)))
        print("actual: {}".format(ptw.dump_tabledata(actual)))

        assert actual == expected

    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "pattern", "is_invert_match", "expected"],
        [
            [
                "multiple_patterns",
                ["test001_AAA", "AAA_test1234", "foo", "AAA_hoge"],
                [[1, 2, 3, 4], [11, 12, 13, 14]],
                ["test[0-9]+", "AAA_[a-z]+"],
                False,
                TableData(
                    "multiple_patterns",
                    ["test001_AAA", "AAA_test1234", "AAA_hoge"],
                    [[1, 2, 4], [11, 12, 14]],
                ),
            ],
            [
                "re_match_pattern",
                HEADER_LIST,
                VALUE_MATRIX,
                ["abc*"],
                False,
                TableData("re_match_pattern", ["abcde"], [[1], [3]]),
            ],
            [
                "re_invert_match_pattern",
                HEADER_LIST,
                VALUE_MATRIX,
                ["abc*"],
                True,
                TableData("re_invert_match_pattern", ["test"], [[2], [4]]),
            ],
            [
                "re_invert_unmatch_pattern",
                HEADER_LIST,
                VALUE_MATRIX,
                ["unmatch_pattern"],
                True,
                TableData("re_invert_unmatch_pattern", HEADER_LIST, VALUE_MATRIX),
            ],
        ],
    )
    def test_normal_re_match(
        self, table_name, header_list, record_list, pattern, is_invert_match, expected
    ):
        tabledata = TableData(table_name, header_list, record_list)
        actual = tabledata.filter_column(
            pattern_list=pattern, is_invert_match=is_invert_match, is_re_match=True
        )

        print("expected: {}".format(ptw.dump_tabledata(expected)))
        print("actual: {}".format(ptw.dump_tabledata(actual)))

        assert actual == expected

    @pytest.mark.parametrize(
        ["table_name", "header_list", "record_list", "pattern", "is_invert_match", "expected"],
        [
            [
                "match_and",
                ["test001_AAA", "AAA_test1234", "foo", "AAA_hoge"],
                [[1, 2, 3, 4], [11, 12, 13, 14]],
                ["[0-9]+", "AAA"],
                False,
                TableData("match_and", ["test001_AAA", "AAA_test1234"], [[1, 2], [11, 12]]),
            ],
            [
                "unmatch_and",
                ["test001_AAA", "AAA_test1234", "foo", "AAA_hoge"],
                [[1, 2, 3, 4], [11, 12, 13, 14]],
                ["1234", "hoge"],
                True,
                TableData("unmatch_and", ["test001_AAA", "foo"], [[1, 3], [11, 13]]),
            ],
        ],
    )
    def test_normal_pattern_match(
        self, table_name, header_list, record_list, pattern, is_invert_match, expected
    ):
        tabledata = TableData(table_name, header_list, record_list)
        actual = tabledata.filter_column(
            pattern_list=pattern,
            is_invert_match=is_invert_match,
            is_re_match=True,
            pattern_match=PatternMatch.AND,
        )

        print("expected: {}".format(ptw.dump_tabledata(expected)))
        print("actual: {}".format(ptw.dump_tabledata(actual)))

        assert actual == expected

    @pytest.mark.parametrize(
        [
            "table_name",
            "header_list",
            "record_list",
            "pattern",
            "is_invert_match",
            "is_re_match",
            "expected",
        ],
        [
            [
                "unmatch_pattern",
                HEADER_LIST,
                VALUE_MATRIX,
                ["abc"],
                False,
                False,
                TableData("unmatch_pattern", [], []),
            ]
        ],
    )
    def test_normal_unmatch(
        self, table_name, header_list, record_list, pattern, is_invert_match, is_re_match, expected
    ):
        tabledata = TableData(table_name, header_list, record_list)
        actual = tabledata.filter_column(
            pattern_list=pattern, is_invert_match=is_invert_match, is_re_match=is_re_match
        )

        assert actual == expected
