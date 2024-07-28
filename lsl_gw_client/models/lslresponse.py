from pydantic import BaseModel, Field
from uuid import UUID
import re

from lsl_gw_lib.models import Avatar
from lsl_gw_lib.models import Region

# choose different http request mechanism for unit tests
import os
if os.getenv('UNIT_TESTS'):
	from tests.fakes.http import ClientResponse
else:
	from aiohttp import ClientResponse


# LinkSet API responses model
class LSLResponse(BaseModel):
	# info from X-SecondLife-* headers:
	objectKey: UUID
	objectName: str = Field(pattern=r'[\x20-\x7b\x7d-\x7e]{0, 63}')
	owner: Avatar
	position: tuple[float, float, float]
	rotation: tuple[float, float, float, float]
	velocity: tuple[float, float, float]
	region: Region 
	production: bool

	# response (different by API methods)
	data: BaseModel | list[BaseModel]
	# other http headers
	headers: dict[str, str]

	def __init__(self, *args, **kwargs) -> None:
		# constructor by http response and parsed data
		if len(args) == 2 and isinstance(args[0], ClientResponse)\
				and isinstance(args[1], BaseModel | list):
			headers: dict[str, str] = dict()
			for headName in args[0].headers:
				if not headName.startswith('X-SecondLife'):
					headers[headName] = args[0].headers[headName]
			super().__init__(
				owner=Avatar(args[0].headers['X-SecondLife-Owner-Key'],
							args[0].headers['X-SecondLife-Owner-Name']),
				objectKey=UUID(args[0].headers['X-SecondLife-Object-Key']),
				objectName=args[0].headers['X-SecondLife-Object-Name'],
				position=re.sub(r'(\(|\))', '', args[0].headers['X-SecondLife-Local-Position']).split(','),
				rotation=re.sub(r'(\(|\))', '', args[0].headers['X-SecondLife-Local-Rotation']).split(','),
				velocity=re.sub(r'(\(|\))', '', args[0].headers['X-SecondLife-Local-Velocity']).split(','),
				region=Region(args[0].headers['X-SecondLife-Region']),
				production=args[0].headers['X-SecondLife-Shard'] == 'Production',
				data=args[1], headers=headers
			)
		else:
			super().__init__(**kwargs)

