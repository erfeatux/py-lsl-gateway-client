from pydantic import validate_call, Field
from typing_extensions import Annotated
from uuid import UUID, uuid5
import re

# choose different http request mechanism for unit tests
import os
if os.getenv('UNIT_TESTS'):
	from tests.fakes.http import get
else:
	from .http import get

from .models import LSLResponse
from lsl_gw_lib.models import LinkSetInfo, PrimInfo, Avatar


# provides API for server.lsl inworld
class LinkSet:
	__urlPattern=re.compile(r'^https://[-a-z0-9@:%_\+~#=]{1,255}\.agni\.secondlife\.io:12043/cap/'
						+ r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
	__url: str

	# contructor by LSLHttp url
	@validate_call
	def __init__(self, url: Annotated[str, Field(pattern=__urlPattern)]) -> None:
		self.__url = url.lower()

	# API info method
	async def info(self) -> LSLResponse:
		resp = await get(f'{self.__url}/info')
		body = (await resp.text()).split('¦')
		return LSLResponse(resp, LinkSetInfo(
				owner=Avatar(resp.headers['X-SecondLife-Owner-Key'],
							resp.headers['X-SecondLife-Owner-Name']),
				lastOwnerId=UUID(body[0]),
				creatorId=UUID(body[1]),
				groupId=UUID(body[2]),
				name=resp.headers['X-SecondLife-Object-Name'],
				description=body[3],
				attached=body[4],
				primsNum=body[5],
				inventoryNum=body[6],
				createdAt = body[7],
				rezzedAt = body[8],
				scriptName = body[9]
			))

	# API prims method
	async def prims(self) -> LSLResponse:
		# list of downloaded prims info
		prims: list[PrimInfo] = list()
		# already used ids (for exclude doubles)
		ids: list[UUID] = list()

		# converts string returned by server.lsl to PrimInfo model
		def primInfo(info) -> PrimInfo:
			# gen unique id for every prim in linkset
			def primId(creator: str, created: str) -> UUID:
				tmpId = uuid5(UUID(creator), created)
				n = 0
				while tmpId in ids:
					tmpId = uuid5(UUID(creator), f'{created}{n}')
					n+=1
				ids.append(tmpId)
				return tmpId
			pId = primId(info[0], info[3])
			return PrimInfo(id=pId, creatorId=info[0], createdAt=info[3], name=info[1], description=info[2])

		# load first part from server.lsl
		resp = await get(f'{self.__url}/prims')
		body = (await resp.text()).splitlines()
		for line in body:
			if line != '+':
				prims.append(primInfo(line.split('¦')))

		# load next parts while exists
		while body[-1] == '+':
			resp = await get(f'{self.__url}/prims/{len(prims)+1}')
			body = (await resp.text()).splitlines()
			for line in body:
				if line != '+':
					prims.append(primInfo(line.split('¦')))

		return LSLResponse(resp, prims)
