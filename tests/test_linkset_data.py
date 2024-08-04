import os
import pytest
import asyncio


def clean(ls, keys: list[str | tuple[str, str]]) -> None:
    for key in keys:
        try:
            if isinstance(key, tuple):
                asyncio.run(ls.linksetDataDelete(key[0], key[1]))
            else:
                asyncio.run(ls.linksetDataDelete(key))
        except Exception:
            pass


@pytest.mark.unitstest
def test_get_keys(setup_env):
    assert os.getenv("UNIT_TESTS")
    from lslgwclient import LinkSet

    ls = LinkSet(
        "https://simhost-0123456789abcdef0.agni.secondlife.io:12043"
        + "/cap/00000000-0000-0000-0000-000000000000"
    )
    resp = asyncio.run(ls.linksetDataKeys())

    assert len(resp.data) == 10
    for i in range(10):
        assert resp.data[i] == f"key{i}"


@pytest.mark.integrationtest
def test_integration_keys(integration_test_url):
    from lslgwclient import LinkSet

    ls = LinkSet(integration_test_url)
    # clean
    clean(ls, ["testkey0", ("testkey1", "pass")])
    # make testing keys
    asyncio.run(ls.linksetDataWrite("testkey0", "testval0"))
    asyncio.run(ls.linksetDataWrite("testkey1", "testval1", "pass"))

    # search keys
    resp = asyncio.run(ls.linksetDataKeys())
    assert "testkey0" in resp.data
    assert "testkey1" in resp.data

    # clean
    clean(ls, ["testkey0", ("testkey1", "pass")])


@pytest.mark.unitstest
def test_read(setup_env):
    assert os.getenv("UNIT_TESTS")
    from lslgwclient import LinkSet
    from lslgwclient.exceptions.linksetdata import LinksetDataNotFoundException

    ls = LinkSet(
        "https://simhost-0123456789abcdef0.agni.secondlife.io:12043"
        + "/cap/00000000-0000-0000-0000-000000000000"
    )

    resp = asyncio.run(ls.linksetDataGet("testkey"))
    assert resp.data == "testval"

    resp = asyncio.run(ls.linksetDataGet("testpkey", "pass"))
    assert resp.data == "testpval"

    with pytest.raises(LinksetDataNotFoundException):
        resp = asyncio.run(ls.linksetDataGet("notexistkey"))


@pytest.mark.integrationtest
def test_integration_read(integration_test_url):
    from lslgwclient import LinkSet
    from lslgwclient.exceptions.linksetdata import LinksetDataNotFoundException

    ls = LinkSet(integration_test_url)
    # clean
    clean(ls, ["testkey0", ("testkey1", "pass")])
    # make testing keys
    asyncio.run(ls.linksetDataWrite("testkey0", "testval0"))
    asyncio.run(ls.linksetDataWrite("testkey1", "testval1", "pass"))

    resp = asyncio.run(ls.linksetDataGet("testkey0"))
    assert resp.data == "testval0"
    resp = asyncio.run(ls.linksetDataGet("testkey1", "pass"))
    assert resp.data == "testval1"

    # clean
    clean(ls, ["testkey0", ("testkey1", "pass"), "unavalaibletestkey"])

    with pytest.raises(LinksetDataNotFoundException):
        resp = asyncio.run(ls.linksetDataGet("unavalaibletestkey"))


@pytest.mark.unitstest
def test_write(setup_env):
    assert os.getenv("UNIT_TESTS")
    from lslgwclient import LinkSet
    from lslgwclient.exceptions.linksetdata import LinksetDataNotUpdatedException

    ls = LinkSet(
        "https://simhost-0123456789abcdef0.agni.secondlife.io:12043"
        + "/cap/00000000-0000-0000-0000-000000000000"
    )

    resp = asyncio.run(ls.linksetDataWrite("testkey", "testval"))
    assert resp.data is None

    resp = asyncio.run(ls.linksetDataWrite("testpkey", "testpval", "pass"))
    assert resp.data is None

    with pytest.raises(LinksetDataNotUpdatedException):
        resp = asyncio.run(ls.linksetDataWrite("alreadyexist", "testval"))


@pytest.mark.integrationtest
def test_integration_write(integration_test_url):
    from lslgwclient import LinkSet
    from lslgwclient.exceptions.linksetdata import LinksetDataNotUpdatedException

    ls = LinkSet(integration_test_url)
    # clean
    clean(ls, ["testkey0", ("testkey1", "pass")])
    # make testing keys
    asyncio.run(ls.linksetDataWrite("testkey0", "testval0"))
    asyncio.run(ls.linksetDataWrite("testkey1", "testval1", "pass"))

    resp = asyncio.run(ls.linksetDataGet("testkey0"))
    assert resp.data == "testval0"
    resp = asyncio.run(ls.linksetDataGet("testkey1", "pass"))
    assert resp.data == "testval1"

    with pytest.raises(LinksetDataNotUpdatedException):
        asyncio.run(ls.linksetDataWrite("testkey0", "testval0"))
    with pytest.raises(LinksetDataNotUpdatedException):
        asyncio.run(ls.linksetDataWrite("testkey1", "testval1", "pass"))

    # clean
    clean(ls, ["testkey0", ("testkey1", "pass"), "unavalaibletestkey"])


@pytest.mark.unitstest
def test_delete(setup_env):
    assert os.getenv("UNIT_TESTS")
    from lslgwclient import LinkSet
    from lslgwclient.exceptions.linksetdata import LinksetDataNotFoundException

    ls = LinkSet(
        "https://simhost-0123456789abcdef0.agni.secondlife.io:12043"
        + "/cap/00000000-0000-0000-0000-000000000000"
    )

    resp = asyncio.run(ls.linksetDataDelete("testkey"))
    assert resp.data is None

    resp = asyncio.run(ls.linksetDataDelete("testpkey", "pass"))
    assert resp.data is None

    with pytest.raises(LinksetDataNotFoundException):
        resp = asyncio.run(ls.linksetDataDelete("notexistkey"))


@pytest.mark.integrationtest
def test_integration_delete(integration_test_url):
    from lslgwclient import LinkSet
    from lslgwclient.exceptions.linksetdata import (
        LinksetDataNotFoundException,
        LinksetDataProtectedException,
    )

    ls = LinkSet(integration_test_url)
    # clean
    clean(ls, ["testkey0", ("testkey1", "pass")])
    # make testing keys
    asyncio.run(ls.linksetDataWrite("testkey0", "testval0"))
    asyncio.run(ls.linksetDataWrite("testkey1", "testval1", "pass"))

    with pytest.raises(LinksetDataProtectedException):
        resp = asyncio.run(ls.linksetDataDelete("testkey0", "pass"))
    resp = asyncio.run(ls.linksetDataDelete("testkey0"))
    assert resp.data is None
    with pytest.raises(LinksetDataProtectedException):
        resp = asyncio.run(ls.linksetDataDelete("testkey1"))
    resp = asyncio.run(ls.linksetDataDelete("testkey1", "pass"))
    assert resp.data is None

    with pytest.raises(LinksetDataNotFoundException):
        resp = asyncio.run(ls.linksetDataDelete("unavalaibletestkey"))
