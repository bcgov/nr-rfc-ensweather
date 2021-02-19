import pytest
import sys
import os
base = '/'.join(__file__.split('/')[:-3])
if base not in sys.path:
    sys.path.append(base)

from src.config import general_settings as gs


@pytest.mark.integration
class Test_Integration:

    def test_true(self):
        assert True


@pytest.mark.unit
class Test_Unit:

    def test_true(self):
        assert True


@pytest.mark.pre_commit
class Test_Pre_Commit:

    def test_true(self):
        assert True

    def test_general(self):
        # Ensure that settings changed for the purposes of testing do not get committed
        assert gs.MAX_HOURS > 1000
        assert gs.MAX_DOWNLOADS == 10
        assert gs.MAX_RETRIES == 3


if __name__ == '__main__':
    pytest.main()
