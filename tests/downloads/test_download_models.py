import pytest
import sys
import shutil
import os
from collections import namedtuple
from glob import glob

import platform
if platform.system() == 'Windows':
    splitter = '\\'
else:
    splitter = '/'

base = splitter.join(__file__.split(splitter)[:-3])
if base not in sys.path:
    sys.path.append(base)

from src.downloads import download_models as dm
from src.processing import regrid_model_data as rg
from src.ens_processing import find_run_time
from src.config import general_settings as gs
from src.config import model_settings as ms
from src.common import helpers as h


@pytest.mark.integration
class Test_Integration:

    def test_true(self):
        assert True

    def test_download_and_regrid(self, monkeypatch):
        T = namedtuple('args', ['run'])
        args = T(run=None)
        rt = find_run_time(args)
        stations = h.get_stations()

        monkeypatch.setattr(dm.gs, 'DIR', gs.DIR + 'integration_test_folder/')
        models = ms.models
        models['geps']['times'] = [6]
        monkeypatch.setattr(rg.ms, 'models', models)

        dm.main('geps', rt, times=[6])
        files = glob(rt.strftime(f'{gs.DIR}integration_test_folder/models/geps/%Y%m%d%H/*'))
        try:
            assert len(files) == 3
            for i in files:
                assert os.stat(i).st_size > 1000
            rg.ensemble_regrid(rt, 'geps', stations)
            files = glob(rt.strftime(f'{gs.DIR}integration_test_folder/models/geps/%Y%m%d%H/*'))
            assert len(files) == 1
            assert os.stat(files[0]).st_size > 1000
            os.remove(files[0])
            files = glob(f'{gs.DIR}/integration_test_folder/tmp/*')
            assert len(files) == 1
            os.remove(files[0])
        except Exception as _:
            folders = glob(f'{gs.DIR}/integration_test_folder/*')
            for folder in folders:
                shutil.rmtree(folder)
            raise

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
