import os
import pytest


def pytest_addoption(parser):
    parser.addoption("--integration")


def pytest_collection_modifyitems(config, items):
    url = config.getoption("--integration")
    new_items = []
    for item in items:
        utmark = item.get_closest_marker("unitstest")
        itmark = item.get_closest_marker("integrationtest")
        if not url and utmark:
            new_items.append(item)
        if url and itmark:
            new_items.append(item)
    items[:] = new_items


@pytest.fixture(scope="session")
def integration_test_url(request):
    return request.config.getoption("--integration")


# choose different http request mechanism for unit tests
@pytest.fixture(scope="session")
def setup_env(integration_test_url):
    if not integration_test_url:
        os.environ["UNIT_TESTS"] = "true"
