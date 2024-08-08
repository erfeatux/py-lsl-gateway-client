import pytest
import random
import asyncio
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from aiohttp.web_exceptions import HTTPUnprocessableEntity

from lslgwlib.enums import InvetoryType


class Values(BaseModel):
    id: UUID
    date: datetime


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
    print(names)
    assert len(names)

    asyncio.run(ls.inventoryDelete([random.choice(names)]))
    resp = asyncio.run(ls.inventoryRead())
    assert itemsNum - 1 == len(resp.data.items)

    with pytest.raises(HTTPUnprocessableEntity):
        asyncio.run(ls.inventoryDelete(["notexistitem"]))
