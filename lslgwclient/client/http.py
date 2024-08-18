# this module contains the http request mechanism

from typing import Any
import urllib.request
import aiohttp
import os.path
import ssl

from .basehttp import HTTP as BaseHTTP
from .basehttp import ClientResponse as BaseClientResponse

from logging import getLogger

log = getLogger(__name__)

# prepare LindenLab.crt
__llcacrt = "LindenLab.crt"
_sslcontext = None
if not _sslcontext:
    if not os.path.isfile("LindenLab.crt"):
        log.debug("Donwload LindenLab.crt")
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/secondlife/llca/master/LindenLab.crt",
            __llcacrt,
        )
    _sslcontext = ssl.create_default_context(cafile=__llcacrt)
    _sslcontext.set_ciphers("ALL:@SECLEVEL=1")


# wrap aiohttp.ClientResponse
class ClientResponse(BaseClientResponse):
    __resp: aiohttp.ClientResponse

    def __init__(self, resp: aiohttp.ClientResponse) -> None:
        self.__resp = resp
        self.headers = dict(resp.headers)

    async def text(self) -> str:
        return await self.__resp.text()

    @property
    def status(self) -> int:
        return self.__resp.status

    @property
    def reason(self) -> str | None:
        return self.__resp.reason


# default HTTP implementation, provides by dependency-injector
class HTTP(BaseHTTP):
    # http get method
    @staticmethod
    async def get(url: str, headers: dict[str, Any] = dict()) -> ClientResponse:
        log.debug(f"get: {url=}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=_sslcontext, headers=headers) as resp:
                log.debug(f"{resp}{await resp.text()}")
                if resp.status not in range(200, 203):
                    e = await HTTP.__exceptionByResp(resp)
                    log.error(e)
                    raise e
                return ClientResponse(resp)

    # http post method
    @staticmethod
    async def post(
        url: str, data: str | None, headers: dict[str, Any] = dict()
    ) -> ClientResponse:
        log.debug(f"post: {url=}; {data=}")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data=data, ssl=_sslcontext, headers=headers
            ) as resp:
                await resp.text()
                if resp.status not in range(200, 203):
                    e = await HTTP.__exceptionByResp(resp)
                    log.error(e)
                    raise e
                return ClientResponse(resp)
