import pytest
import asyncio
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from lslgwlib.models import PrimInfo


class Values(BaseModel):
    id: UUID
    date: datetime


@pytest.mark.unitstest
def test_get_prims(api, units_test_url):
    ls = api.linkset(units_test_url)
    resp0 = asyncio.run(ls.prims())
    resp1 = asyncio.run(ls.prims())

    for prims in zip(resp0.data, resp1.data):
        assert prims[0].id == prims[1].id


@pytest.mark.integrationtest
def test_integration_get_prims(api, integration_test_url):
    ls = api.linkset(integration_test_url)
    resp = asyncio.run(ls.prims())
    assert isinstance(resp.data, list)
    if len(resp.data):
        ids: list[UUID] = list()
        for prim in resp.data:
            assert isinstance(prim, PrimInfo)
            assert prim.id.int  # not NULL_KEY
            assert prim.id not in ids  # not a duplicate
            ids.append(prim.id)
