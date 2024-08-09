import pytest
import random
import asyncio
from copy import copy
from uuid import uuid4, UUID
from pydantic import ValidationError
from aiohttp.web_exceptions import (
    HTTPUnprocessableEntity,
    HTTPForbidden,
    HTTPBadRequest,
)

from lslgwlib.enums import InvetoryType


@pytest.mark.unitstest
def test_read_inventory(api, units_test_url):
    ls = api.linkset(units_test_url)
    resp = asyncio.run(ls.inventoryRead())
    assert len(resp.data.items) == 4
    resp = asyncio.run(ls.inventoryRead(InvetoryType.NOTECARD))
    assert len(resp.data.items) == 2


@pytest.mark.integrationtest
def test_integration_read_inventory(api, integration_test_url):
    ls = api.linkset(integration_test_url)
    resp = asyncio.run(ls.info())
    scriptName = resp.data.scriptName
    ownerId = resp.data.owner.id
    resp = asyncio.run(ls.inventoryRead())
    assert resp.data.byName(scriptName).creatorId == ownerId


@pytest.mark.unitstest
def test_delete_inventory(api, units_test_url):
    ls = api.linkset(units_test_url)
    asyncio.run(
        ls.inventoryDelete(
            ["verrryyyyyyloooooongitemname{:05d}".format(x) for x in range(100)]
        )
    )
    with pytest.raises(HTTPUnprocessableEntity):
        asyncio.run(ls.inventoryDelete(["notexistitem"]))


@pytest.mark.integrationtest
def test_integration_delete_inventory(api, integration_test_url):
    ls = api.linkset(integration_test_url)
    resp = asyncio.run(ls.info())
    scriptName = resp.data.scriptName
    resp = asyncio.run(ls.inventoryRead())
    itemsNum = len(resp.data.items)
    names = resp.data.names()
    names.remove(scriptName)
    assert len(names)

    asyncio.run(ls.inventoryDelete([random.choice(names)]))
    resp = asyncio.run(ls.inventoryRead())
    assert itemsNum - 1 == len(resp.data.items)

    with pytest.raises(HTTPUnprocessableEntity):
        asyncio.run(ls.inventoryDelete(["notexistitem"]))


@pytest.mark.unitstest
def test_give_inventory(api, units_test_url):
    ls = api.linkset(units_test_url)
    asyncio.run(ls.inventoryGive(uuid4(), "itemname"))
    with pytest.raises(HTTPUnprocessableEntity):
        asyncio.run(ls.inventoryGive(uuid4(), "notexistitem"))
    with pytest.raises(ValueError):
        asyncio.run(ls.inventoryGive(UUID(int=0), "itemname"))


@pytest.mark.integrationtest
def test_integration_give_inventory(api, integration_test_url):
    ls = api.linkset(integration_test_url)
    resp = asyncio.run(ls.info())
    scriptName = resp.data.scriptName
    ownerId = resp.data.owner.id
    resp = asyncio.run(ls.inventoryRead())
    names = resp.data.names()
    names.remove(scriptName)
    notransferables = copy(names)
    for item in resp.data.items:
        if item.name != scriptName:
            if item.permissions.owner.TRANSFER:
                notransferables.remove(item.name)
            else:
                names.remove(item.name)
    assert len(names)
    assert len(notransferables)

    asyncio.run(ls.inventoryGive(ownerId, random.choice(names)))

    with pytest.raises(HTTPForbidden):
        asyncio.run(ls.inventoryGive(ownerId, random.choice(notransferables)))
    with pytest.raises(HTTPUnprocessableEntity):
        asyncio.run(ls.inventoryGive(ownerId, "notexistitem"))


@pytest.mark.unitstest
def test_give_inventory_list(api, units_test_url):
    ls = api.linkset(units_test_url)
    asyncio.run(ls.inventoryGiveList(uuid4(), "foldername", ["itemname"]))
    with pytest.raises(HTTPUnprocessableEntity):
        asyncio.run(ls.inventoryGiveList(uuid4(), "foldername", ["notexistitem"]))
    with pytest.raises(ValueError):
        asyncio.run(ls.inventoryGiveList(UUID(int=0), "foldername", ["item"]))
    with pytest.raises(ValidationError):
        asyncio.run(ls.inventoryGiveList(UUID(int=0), "foldername" * 7, ["item"]))
    with pytest.raises(ValueError):
        asyncio.run(
            ls.inventoryGiveList(
                uuid4(),
                "foldername",
                ["verrryyyyyyloooooongitemname{:032d}".format(x) for x in range(41)],
            )
        )
    with pytest.raises(ValidationError):
        asyncio.run(
            ls.inventoryGiveList(
                uuid4(),
                "foldername",
                ["verrryyyyyyloooooongitemname{:03d}".format(x) for x in range(42)],
            )
        )


@pytest.mark.integrationtest
def test_integration_give_inventory_list(api, integration_test_url):
    ls = api.linkset(integration_test_url)
    resp = asyncio.run(ls.info())
    scriptName = resp.data.scriptName
    ownerId = resp.data.owner.id
    resp = asyncio.run(ls.inventoryRead())
    names = resp.data.names()
    print(scriptName, names)
    names.remove(scriptName)
    notransferables = copy(names)
    for item in resp.data.items:
        if item.name != scriptName:
            if item.permissions.owner.TRANSFER:
                notransferables.remove(item.name)
            else:
                names.remove(item.name)
    assert len(names)
    assert len(notransferables)

    asyncio.run(ls.inventoryGiveList(ownerId, "foldername", names))

    with pytest.raises(HTTPBadRequest):
        asyncio.run(ls.inventoryGiveList(uuid4(), "foldername", names))
    with pytest.raises(HTTPForbidden):
        asyncio.run(
            ls.inventoryGiveList(
                ownerId, "foldername", [random.choice(notransferables)]
            )
        )
    with pytest.raises(HTTPUnprocessableEntity):
        asyncio.run(ls.inventoryGiveList(ownerId, "foldername", ["notexistitem"]))
