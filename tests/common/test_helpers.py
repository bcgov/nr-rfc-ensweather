import pytest
import sys
import os
from datetime import datetime as dt, timedelta

base = '/'.join(__file__.split('/')[:-3])
if base not in sys.path:
    sys.path.append(base)

import pandas as pd

from src.common import helpers as h


@pytest.mark.integration
class Test_Integration:

    def test_true(self):
        assert True


@pytest.mark.unit
class Test_Unit:

    def test_true(self):
        assert True

    def test_free_range(self):
        produced = []
        expected = [dt(2020, 1, 1), dt(2020, 1, 2), dt(2020, 1, 3)]
        for tm in h.free_range(dt(2020, 1, 1), dt(2020, 1, 4), timedelta(days=1)):
            produced.append(tm)
        assert produced == expected


@pytest.mark.pre_commit
class Test_Pre_Commit:

    def test_true(self):
        assert True


if __name__ == '__main__':
    pytest.main()
