import pytest
import sys
import os
base = '/'.join(__file__.split('/')[:-3])
if base not in sys.path:
    sys.path.append(base)

import pandas as pd

from src.processing import regrid_model_data as rmd


@pytest.mark.integration
class Test_Integration:

    def test_true(self):
        assert True


@pytest.mark.unit
class Test_Unit:

    def test_true(self):
        assert True

    def test_convert_location_to_wgrib2(self):
        stations = pd.DataFrame({
            'latitude': [49.9, 38.2, 56.1],
            'longitude': [-97.2, -110.1, 120.0],
        })
        ret = rmd.convert_location_to_wgrib2(stations)
        exp = '-97.2:49.9:-110.1:38.2:120.0:56.1'
        assert ret == exp


@pytest.mark.pre_commit
class Test_Pre_Commit:

    def test_true(self):
        assert True


if __name__ == '__main__':
    pytest.main()
