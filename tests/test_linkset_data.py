import os
import pytest
import asyncio


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


def test_read(setup_env):
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


def test_write(setup_env):
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


def test_delete(setup_env):
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
