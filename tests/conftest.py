import os
import pytest


# choose different http request mechanism for unit tests
@pytest.fixture(scope="session")
def setup_env():
    os.environ["UNIT_TESTS"] = "true"
