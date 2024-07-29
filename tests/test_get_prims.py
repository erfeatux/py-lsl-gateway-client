import pytest
import asyncio
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class Values(BaseModel):
	id: UUID
	date: datetime


def test_get_prims(setup_env):
	from lslgwclient import LinkSet

	ls = LinkSet('https://simhost-0123456789abcdef0.agni.secondlife.io:12043'
			+ '/cap/00000000-0000-0000-0000-000000000000')
	resp0 = asyncio.run(ls.prims())
	resp1 = asyncio.run(ls.prims())

	for prims in zip(resp0.data, resp1.data):
		assert prims[0].id == prims[1].id
