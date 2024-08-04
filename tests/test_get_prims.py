import os
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
def test_get_prims(setup_env):
    assert os.getenv("UNIT_TESTS")
    from lslgwclient import LinkSet

    ls = LinkSet(
        "https://simhost-0123456789abcdef0.agni.secondlife.io:12043"
        + "/cap/00000000-0000-0000-0000-000000000000"
    )
    resp0 = asyncio.run(ls.prims())
    resp1 = asyncio.run(ls.prims())

    for prims in zip(resp0.data, resp1.data):
        assert prims[0].id == prims[1].id


@pytest.mark.integrationtest
def test_integration_get_prims(integration_test_url):
    from lslgwclient import LinkSet

    ls = LinkSet(integration_test_url)
    resp = asyncio.run(ls.prims())
    assert isinstance(resp.data, list)
    if len(resp.data):
        ids: list[UUID] = list()
        for prim in resp.data:
            assert isinstance(prim, PrimInfo)
            assert prim.id.int  # not NULL_KEY
            assert prim.id not in ids  # not a duplicate
            ids.append(prim.id)
