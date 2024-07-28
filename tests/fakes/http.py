# this module contains the http request mechanism
# fake for unit tests

from uuid import uuid4

creatorId = uuid4()

class ClientResponse:
	__text: str
	headers: dict[str, str] = {
			'Date': 'Sat, 27 Jul 2024 22:38:52 GMT',
			'Server': 'Second Life LSL/Second Life Server 2024-06-11.9458617693 (http://secondlife.com)',
			'X-LL-Request-Id': 'ZqV2_NCg1ZQVEy3NK2hjeQAAA40',
			'Content-Length': '205',
			'Cache-Control': 'no-cache, max-age=0',
			'Content-Type': 'text/plain; charset=utf-8',
			'Pragma': 'no-cache',
			'X-SecondLife-Local-Position': '(50.362698, 39.342766, 1000.523254)',
			'X-SecondLife-Local-Rotation': '(0.000000, 0.000000, 0.000000, 1.000000)',
			'X-SecondLife-Local-Velocity': '(0.000000, 0.000000, 0.000000)',
			'X-SecondLife-Object-Key': '00000000-0000-0000-0000-000000000000',
			'X-SecondLife-Object-Name': 'Test object name',
			'X-SecondLife-Owner-Key': '00000000-0000-0000-0000-000000000000',
			'X-SecondLife-Owner-Name': 'FName LName',
			'X-SecondLife-Region': 'Region Name (256, 512)',
			'X-SecondLife-Shard': 'Testing',
			'Access-Control-Allow-Origin': '*',
			'Connection': 'close'
		}

	def __init__(self, text: str) -> None:
		self.__text = text

	async def text(self) -> str:
		return self.__text


# http get method
async def get(url: str) -> ClientResponse:
	match url.lower():
		# fake data for info method
		case url if url.endswith('/info'):
			return ClientResponse('00000000-0000-0000-0000-000000000000¦'
						+ '00000000-0000-0000-0000-000000000000¦00000000-0000-0000-0000-000000000000¦'
						+ 'test description¦0¦255¦1¦2023-11-28T20:47:54.389906Z¦'
						+ '2023-11-28T20:47:54.389906Z¦script.lsl')
		# fake data for first call of prims method
		case url if url.endswith('/prims'):
			return ClientResponse(f'{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z'
							+ f'\n{creatorId}¦Test prim name¦test prim desc¦2023-10-28T20:47:54.389906Z'
							+ f'\n{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z'
							+ f'\n{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z'
							+ f'\n{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z'
							+ f'\n{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:57:54.389906Z\n+')
		# fake data for second call of prims method
		case url if url.endswith('/prims/7'):
			return ClientResponse(f'{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z'
							+ f'\n{creatorId}¦Test last prim¦test prim desc¦2023-11-28T20:57:54.389906Z')
	return ClientResponse('')
