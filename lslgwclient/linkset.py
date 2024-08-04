from pydantic import validate_call, Field
from typing_extensions import Annotated
from uuid import UUID, uuid5
import re

# choose different http request mechanism for unit tests
import os

if os.getenv("UNIT_TESTS"):
    from tests.fakes.http import get, post
else:
    from .http import get, post

from .models import LSLResponse
from .exceptions import linksetDataExceptionByNum
from lslgwlib.models import LinkSetInfo, PrimInfo, Avatar


# provides API for server.lsl inworld
class LinkSet:
    __urlPattern = re.compile(
        r"^https://[-a-z0-9@:%_\+~#=]{1,255}\.agni\.secondlife\.io:12043/cap/"
        + r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    __url: str

    # contructor by LSLHttp url
    @validate_call
    def __init__(self, url: Annotated[str, Field(pattern=__urlPattern)]) -> None:
        self.__url = url.lower()

    # API info method
    async def info(self) -> LSLResponse:
        resp = await get(f"{self.__url}/info")
        body = (await resp.text()).split("¦")
        return LSLResponse(
            resp,
            LinkSetInfo(
                owner=Avatar(
                    resp.headers["X-SecondLife-Owner-Key"],
                    resp.headers["X-SecondLife-Owner-Name"],
                ),
                lastOwnerId=UUID(body[0]),
                creatorId=UUID(body[1]),
                groupId=UUID(body[2]),
                name=resp.headers["X-SecondLife-Object-Name"],
                description=body[3],
                attached=body[4],
                primsNum=body[5],
                inventoryNum=body[6],
                createdAt=body[7],
                rezzedAt=body[8],
                scriptName=body[9],
            ),
        )

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
                    tmpId = uuid5(UUID(creator), f"{created}{n}")
                    n += 1
                ids.append(tmpId)
                return tmpId

            pId = primId(info[0], info[3])
            return PrimInfo(
                id=pId,
                creatorId=info[0],
                createdAt=info[3],
                name=info[1],
                description=info[2],
            )

        # load first part from server.lsl
        resp = await get(f"{self.__url}/prims")
        body = (await resp.text()).splitlines()
        for line in body:
            if line != "+":
                prims.append(primInfo(line.split("¦")))

        # load next parts while exists
        while body and body[-1] == "+":
            resp = await get(f"{self.__url}/prims/{len(prims)+1}")
            body = (await resp.text()).splitlines()
            for line in body:
                if line != "+":
                    prims.append(primInfo(line.split("¦")))

        return LSLResponse(resp, prims)

    # get all linkset data keys
    async def linksetDataKeys(self) -> LSLResponse:
        keys: list[str] = list()
        resp = await get(f"{self.__url}/linksetdata/keys")
        text = await resp.text()
        if not text:
            return LSLResponse(resp, keys)
        body = text.split("¦")
        if body[-1] == "+":
            keys.extend(body[:-1])
        else:
            keys.extend(body)
        while body[-1] == "+":
            resp = await get(f"{self.__url}/linksetdata/keys/{len(keys)+1}")
            body = (await resp.text()).split("¦")
            if body[-1] == "+":
                keys.extend(body[:-1])
            else:
                keys.extend(body)
        return LSLResponse(resp, keys)

    # get linkset data value by key
    @validate_call
    async def linksetDataGet(
        self, key: Annotated[str, Field(min_length=1)], pwd: str | None = None
    ) -> LSLResponse:
        if pwd:
            resp = await post(f"{self.__url}/linksetdata/read/{key}", pwd)
        else:
            resp = await get(f"{self.__url}/linksetdata/read/{key}")
        if not await resp.text():
            raise linksetDataExceptionByNum(4, key)
        return LSLResponse(resp, await resp.text())

    # set linkset data value
    @validate_call
    async def linksetDataWrite(
        self,
        key: Annotated[str, Field(min_length=1)],
        value: Annotated[str, Field(min_length=1)],
        pwd: str | None = None,
    ) -> LSLResponse:
        if pwd:
            resp = await post(f"{self.__url}/linksetdata/write/{key}", f"{value}¦{pwd}")
        else:
            resp = await post(f"{self.__url}/linksetdata/write/{key}", value)
        num = int(await resp.text())
        if num:
            raise linksetDataExceptionByNum(num, key)
        return LSLResponse(resp, None)

    # delete linkset data value by key
    @validate_call
    async def linksetDataDelete(
        self,
        key: Annotated[str, Field(min_length=1)],
        pwd: str | None = None,
    ) -> LSLResponse:
        resp = await post(f"{self.__url}/linksetdata/delete/{key}", pwd)
        num = int(await resp.text())
        if num:
            raise linksetDataExceptionByNum(num, key)
        return LSLResponse(resp, None)
