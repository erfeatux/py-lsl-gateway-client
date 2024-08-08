import pytest
import asyncio
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

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
