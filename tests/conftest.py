import pytest

from lslgwclient import API


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
def api(integration_test_url):
    api = API()
    if not integration_test_url:
        from tests.fakes.http import HTTP

        api.container.http.override(HTTP)

    return api


@pytest.fixture(scope="session")
def units_test_url():
    return (
        "https://simhost-0123456789abcdef0.agni.secondlife.io:12043"
        + "/cap/00000000-0000-0000-0000-000000000000"
    )
