import pytest
import asyncio
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class Values(BaseModel):
	id: UUID
	date: datetime


def test_get_info(setup_env):
	from lsl_gw_client import LinkSet

	ls = LinkSet('https://simhost-0123456789abcdef0.agni.secondlife.io:12043'
			+ '/cap/00000000-0000-0000-0000-000000000000')
	resp = asyncio.run(ls.info())

	tvs = Values(id='00000000-0000-0000-0000-000000000000', date='2023-11-28T20:47:54.389906Z')
	assert resp.data.owner.id == tvs.id
	assert resp.data.owner.modernName() == 'fname.lname'
	assert resp.data.lastOwnerId == tvs.id
	assert resp.data.creatorId == tvs.id
	assert resp.data.groupId == tvs.id
	assert resp.data.name == 'Test object name'
	assert resp.data.description == 'test description'
	assert resp.data.attached == 0
	assert resp.data.primsNum == 255
	assert resp.data.inventoryNum == 1
	assert resp.data.createdAt == tvs.date
	assert resp.data.rezzedAt == tvs.date
	assert resp.data.scriptName == 'script.lsl'
