import pytest
import sys
import os
base = '/'.join(__file__.split('/')[:-3])
if base not in sys.path:
    sys.path.append(base)

from src.downloads import download_models as dm
from src.config import general_settings as gs


@pytest.mark.integration
class Test_Integration:

    def test_true(self):
        assert True


@pytest.mark.unit
class Test_Unit:

    def test_true(self):
        assert True

    @pytest.mark.parametrize(
        'expected, expected_result',
        (
            [5, True],
            [8, False],
            [2, True],
            [6, True],
        )
    )
    def test_check_downloads(self, expected, expected_result):
        folder = gs.DIR + 'tests/resources/mock_folder/*'
        assert dm.check_downloads(folder, expected, file_size=4) == expected_result


@pytest.mark.pre_commit
class Test_Pre_Commit:

    def test_true(self):
        assert True


if __name__ == '__main__':
    pytest.main()
