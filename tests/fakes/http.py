# this module contains the http request mechanism
# fake for unit tests

from uuid import uuid4

from lslgwclient.client.basehttp import HTTP as BaseHTTP
from lslgwclient.client.basehttp import ClientResponse as BaseClientResponse

creatorId = uuid4()


class ClientResponse(BaseClientResponse):
    __text: str
    headers: dict[str, str] = {
        "Date": "Sat, 27 Jul 2024 22:38:52 GMT",
        "Server": "Second Life LSL/Second Life Server 2024-06-11.9458617693 (http://secondlife.com)",
        "X-LL-Request-Id": "ZqV2_NCg1ZQVEy3NK2hjeQAAA40",
        "Content-Length": "205",
        "Cache-Control": "no-cache, max-age=0",
        "Content-Type": "text/plain; charset=utf-8",
        "Pragma": "no-cache",
        "X-SecondLife-Local-Position": "(50.362698, 39.342766, 1000.523254)",
        "X-SecondLife-Local-Rotation": "(0.000000, 0.000000, 0.000000, 1.000000)",
        "X-SecondLife-Local-Velocity": "(0.000000, 0.000000, 0.000000)",
        "X-SecondLife-Object-Key": "00000000-0000-0000-0000-000000000000",
        "X-SecondLife-Object-Name": "Test object name",
        "X-SecondLife-Owner-Key": "00000000-0000-0000-0000-000000000000",
        "X-SecondLife-Owner-Name": "FName LName",
        "X-SecondLife-Region": "Region Name (256, 512)",
        "X-SecondLife-Shard": "Testing",
        "Access-Control-Allow-Origin": "*",
        "Connection": "close",
    }

    def __init__(self, text: str) -> None:
        self.__text = text

    async def text(self) -> str:
        return self.__text


class HTTP(BaseHTTP):
    # http get method
    @staticmethod
    async def get(url: str) -> ClientResponse:
        match url.lower():
            # fake data for info method
            case url if url.endswith("/info"):
                return ClientResponse(
                    "00000000-0000-0000-0000-000000000000¦"
                    + "00000000-0000-0000-0000-000000000000¦00000000-0000-0000-0000-000000000000¦"
                    + "test description¦0¦255¦1¦2023-11-28T20:47:54.389906Z¦"
                    + "2023-11-28T20:47:54.389906Z¦script.lsl"
                )

            # fake data for first call of prims method
            case url if url.endswith("/prims"):
                return ClientResponse(
                    f"{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z¦4"
                    + f"\n{creatorId}¦Test prim name¦test prim desc¦2023-10-28T20:47:54.389906Z¦4"
                    + f"\n{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z¦4"
                    + f"\n{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z¦4"
                    + f"\n{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z¦4"
                    + f"\n{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:57:54.389906Z¦4\n+"
                )
            # fake data for second call of prims method
            case url if url.endswith("/prims/7"):
                return ClientResponse(
                    f"{creatorId}¦Test prim name¦test prim desc¦2023-11-28T20:47:54.389906Z¦4"
                    + f"\n{creatorId}¦Test last prim¦test prim desc¦2023-11-28T20:57:54.389906Z¦4"
                )

            # fake data for first call of linksetDataKeys method
            case url if url.endswith("/linksetdata/keys"):
                return ClientResponse("key0¦key1¦key2¦key3¦key4¦+")
            # fake data for second call of linksetDataKeys method
            case url if url.endswith("/linksetdata/keys/6"):
                return ClientResponse("key5¦key6¦key7¦key8¦key9")

            # fake data for call of linksetDataGet method
            case url if url.endswith("/linksetdata/read/testkey"):
                return ClientResponse("testval")
            # fake data for call of linksetDataGet method with not exist key
            case url if url.endswith("/linksetdata/read/notexistkey"):
                return ClientResponse("")

        return ClientResponse("")

    # http get method
    @staticmethod
    async def post(url: str, data: str | None) -> ClientResponse:
        match url.lower():
            # fake data for call of linksetDataGet method with protection pass
            case url if url.endswith("/linksetdata/read/testpkey"):
                if data == "pass":
                    return ClientResponse("testpval")

            # fake data for call of linksetDataWrite method
            case url if url.endswith("/linksetdata/write/testkey"):
                if data == "testval":
                    return ClientResponse("0")
            # fake data for call of linksetDataWrite method with already exist key:value
            case url if url.endswith("/linksetdata/write/alreadyexist"):
                if data == "testval":
                    return ClientResponse("5")
            # fake data for call of linksetDataWrite method with protection pass
            case url if url.endswith("/linksetdata/write/testpkey"):
                if data == "testpval¦pass":
                    return ClientResponse("0")

            # fake data for call of linksetDataWrite method
            case url if url.endswith("/linksetdata/delete/testkey"):
                if data is None:
                    return ClientResponse("0")
            # fake data for call of linksetDataWrite method with not exist key
            case url if url.endswith("/linksetdata/delete/notexistkey"):
                if data is None:
                    return ClientResponse("4")
            # fake data for call of linksetDataWrite method with protection pass
            case url if url.endswith("/linksetdata/delete/testpkey"):
                if data == "pass":
                    return ClientResponse("0")

        return ClientResponse("")
