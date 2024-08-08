# this module contains the http request mechanism
# fake for unit tests

from logging import getLogger
from uuid import uuid4
import re

from lslgwclient.client.basehttp import HTTP as BaseHTTP
from lslgwclient.client.basehttp import ClientResponse as BaseClientResponse

creatorId = uuid4()
log = getLogger(__name__)


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
        log.debug(f"{url=}")
        match url.lower():
            # fake data for info method
            case url if url.endswith("/info"):
                return ClientResponse(
                    "00000000-0000-0000-0000-000000000000¦"
                    + "00000000-0000-0000-0000-000000000000¦00000000-0000-0000-0000-000000000000¦"
                    + "test description¦0¦255¦1¦2023-11-28T20:47:54.389906Z¦"
                    + "2023-11-28T20:47:54.389906Z¦script.lsl¦2147483647¦49152¦0¦32768¦0"
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
            # fake data for call of inventoryRead method with notecard type
            case url if "/inventory/read?type=7" in url:
                return ClientResponse(
                    "fd42e87a-44d8-1343-9ecd-fc7dd23f6765¦7¦A&Y Re-delivery issue"
                    + "¦2023-03-03 21:17:52 note card¦bf1d107f-2c7a-4e0b-9cac-d2b30ccd2821"
                    + "¦581632¦581632¦0¦0¦581632¦2024-08-07T00:32:31Z"
                    + "\n0c13f3e7-7d41-5675-ee70-fa9309319f07¦7¦New Note¦2022-05-30 19:59:13 note card"
                    + "¦07ce6a4a-b34e-4e62-96e3-16f2a8b19c89¦2147483647¦2147483647"
                    + "¦0¦0¦581632¦2024-08-07T00:32:31Z"
                )
            # fake data for first call of inventoryRead method
            case url if "/inventory/read?" in url:
                return ClientResponse(
                    "fd42e87a-44d8-1343-9ecd-fc7dd23f6765¦7¦A&Y Re-delivery issue"
                    + "¦2023-03-03 21:17:52 note card¦bf1d107f-2c7a-4e0b-9cac-d2b30ccd2821"
                    + "¦581632¦581632¦0¦0¦581632¦2024-08-07T00:32:31Z"
                    + "\n488c4978-99e3-449a-4c98-5fc221e5a7a5¦0¦A&Y_logo¦(No Description)"
                    + "¦0c2566cd-2ac9-4566-bab4-a3c4bfce58bd¦581632¦581632¦0¦0¦581632¦2024-08-07T00:32:43Z"
                    + "\n0c13f3e7-7d41-5675-ee70-fa9309319f07¦7¦New Note¦2022-05-30 19:59:13 note card"
                    + "¦07ce6a4a-b34e-4e62-96e3-16f2a8b19c89¦2147483647¦2147483647"
                    + "¦0¦0¦581632¦2024-08-07T00:32:31Z\n+"
                )
            # fake data for second call of inventoryRead method
            case url if "/inventory/read" in url:
                return ClientResponse(
                    "00cc5bf5-2e03-8cfa-3c36-fc5b40238d7f¦10¦New Script¦2024-08-07 03:42:12 lsl2 script"
                    + "¦07ce6a4a-b34e-4e62-96e3-16f2a8b19c89¦2147483647¦2147483647"
                    + "¦0¦0¦532480¦2024-08-06T23:42:12Z"
                )

        return ClientResponse("")

    # http get method
    @staticmethod
    async def post(url: str, data: str | None) -> ClientResponse:
        log.debug(f"{url=}; {data=}")
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
