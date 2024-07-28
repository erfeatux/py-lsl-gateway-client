import pytest
import asyncio
from uuid import UUID


def test_lslresponse(setup_env):
	from lsl_gw_client import LinkSet

	ls = LinkSet('https://simhost-0123456789abcdef0.agni.secondlife.io:12043'
			+ '/cap/00000000-0000-0000-0000-000000000000')
	resp = asyncio.run(ls.info())

	nullId = UUID('00000000-0000-0000-0000-000000000000')

	assert resp.objectKey == nullId
	assert resp.objectName == 'Test object name'
	assert resp.owner.id == nullId
	assert resp.owner.modernName() == 'fname.lname'
	assert resp.position == (50.362698, 39.342766, 1000.523254)
	assert resp.rotation == (0.0, 0.0, 0.0, 1.0)
	assert resp.velocity == (0.0, 0.0, 0.0)
	assert str(resp.region) == 'Region Name (256, 512)'
	assert resp.production is False
	assert resp.headers['Date'] == 'Sat, 27 Jul 2024 22:38:52 GMT'
	assert resp.headers['Server'] == 'Second Life LSL/Second Life Server '\
									+ '2024-06-11.9458617693 (http://secondlife.com)'
	assert resp.headers['X-LL-Request-Id'] == 'ZqV2_NCg1ZQVEy3NK2hjeQAAA40'
	assert resp.headers['Content-Length'] == '205'
	assert resp.headers['Cache-Control'] == 'no-cache, max-age=0'
	assert resp.headers['Content-Type'] == 'text/plain; charset=utf-8'
	assert resp.headers['Pragma'] == 'no-cache'
	assert resp.headers['Access-Control-Allow-Origin'] == '*'
	assert resp.headers['Connection'] == 'close'
