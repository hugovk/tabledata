# encoding: utf-8

from __future__ import print_function, unicode_literals

import pytest

from tabledata import set_logger
from tabledata._logger._null_logger import NullLogger


class Test_set_logger(object):
    @pytest.mark.parametrize(["value"], [[True], [False]])
    def test_smoke(self, value):
        set_logger(value)


class Test_NullLogger:
    @pytest.mark.parametrize(["value"], [[True], [False]])
    def test_smoke(self, value, monkeypatch):
        monkeypatch.setattr("tabledata._logger._logger.logger", NullLogger())
        set_logger(value)
