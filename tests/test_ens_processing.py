from datetime import datetime as dt
import pytest
import sys
import os
from collections import namedtuple

import platform
if platform.system() == 'Windows':
    splitter = '\\'
else:
    splitter = '/'

base = splitter.join(__file__.split(splitter)[:-2])
if base not in sys.path:
    sys.path.append(base)

from src import ens_processing as es


@pytest.mark.integration
class Test_Integration:

    def test_true(self):
        assert True


@pytest.mark.unit
class Test_Unit:

    def test_true(self):
        assert True

    @pytest.mark.parametrize(
        'run_input, current_time, exp',
        (
            [None, dt(2020, 1, 1, 19), dt(2020, 1, 1, 12)],
            [None, dt(2020, 1, 1, 7), dt(2020, 1, 1, 0)],
            [None, dt(2020, 1, 1, 1), dt(2019, 12, 31, 12)],
            ['20210101_00', None, dt(2021, 1, 1, 0)],
        )
    )
    def test_find_run_time(self, run_input, current_time, exp, monkeypatch):
        arg_tuple = namedtuple('args', ['run'])
        args = arg_tuple(run=run_input)

        def mock_return():
            return current_time

        monkeypatch.setattr(es, 'get_now', mock_return)
        run_time = es.find_run_time(args)
        assert run_time == exp


@pytest.mark.pre_commit
class Test_Pre_Commit:

    def test_true(self):
        assert True


if __name__ == '__main__':
    pytest.main()
