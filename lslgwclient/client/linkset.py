from typing_extensions import Annotated, Any
from pydantic import validate_call, Field
from uuid import UUID, uuid5
from typing import Sequence
import re

from lslgwclient.models import LSLResponse
from lslgwclient.exceptions import linksetDataExceptionByNum
from lslgwlib.models import (
    LinkSetInfo,
    PrimInfo,
    Avatar,
    Permissions,
    Invetory,
    InvetoryItem,
)
from lslgwlib.enums import InvetoryType
from .basehttp import HTTP

from logging import getLogger, Logger


# provides API for server.lsl inworld
class LinkSet:
    """LinkSet - provides LSL object interaction"""

    __log: Logger = getLogger()
    __urlPattern = re.compile(
        r"^https://[-a-z0-9@:%_\+~#=]{1,255}\.agni\.secondlife\.io:12043/cap/"
        + r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    __headers: dict[str, Any]
    __http: HTTP
    __url: str
    __id: UUID

    # contructor by LSLHttp url
    def __init__(self, http: HTTP, url: str, headers: dict[str, Any] = dict()) -> None:
        if not self.__urlPattern.match(url):
            raise ValueError(f"Invalid url: {url}")
        self.__headers = headers
        self.__url = url.lower()
        self.__http = http
        self.__log.info(url)

    # API info method
    async def info(self) -> LSLResponse:
        """LSL object base stats

        returns LSLResponse.data: LinkSetInfo
        """
        resp = await self.__http.get(f"{self.__url}/info", headers=self.__headers)
        body = (await resp.text()).split("¦")
        lslresp = LSLResponse(
            resp,
            LinkSetInfo(
                id=resp.headers["X-SecondLife-Object-Key"],
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
                permissions=Permissions(*body[10:]),
            ),
        )
        self.__id = lslresp.data.id
        self.__log = getLogger(f"{self.__class__.__name__}({self.__id})")
        self.__log.debug(lslresp.data)
        return lslresp

    # API prims method
    async def prims(self) -> LSLResponse:
        """LSL object linkset prims

        returns LSLResponse.data: list[PrimInfo]
        """
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

            pId = primId(info[0], info[3] + info[4])
            return PrimInfo(
                id=pId,
                creatorId=info[0],
                createdAt=info[3],
                name=info[1],
                description=info[2],
                faces=info[4],
            )

        body = ["+"]

        # load parts while exists
        while body and body[-1] == "+":
            if len(prims):
                resp = await self.__http.get(
                    f"{self.__url}/prims/{len(prims)+1}", headers=self.__headers
                )
            else:
                resp = await self.__http.get(
                    f"{self.__url}/prims", headers=self.__headers
                )
            body = (await resp.text()).splitlines()
            for line in body:
                if line != "+":
                    prims.append(primInfo(line.split("¦")))

        self.__log.debug(f"{len(prims)} prims")
        return LSLResponse(resp, prims)

    # get all linkset data keys
    async def linksetDataKeys(self) -> LSLResponse:
        """LSL object likset data keys

        returns LSLResponse.data: list[str]
        """
        keys: list[str] = list()
        body = ["+"]

        while body[-1] == "+":
            if len(keys):
                resp = await self.__http.get(
                    f"{self.__url}/linksetdata/keys/{len(keys)+1}",
                    headers=self.__headers,
                )
            else:
                resp = await self.__http.get(
                    f"{self.__url}/linksetdata/keys", headers=self.__headers
                )
            body = (await resp.text()).split("¦")
            if body[-1] == "+":
                keys.extend(body[:-1])
            else:
                keys.extend(body)

        self.__log.debug(f"{len(keys)} linkset data keys")
        return LSLResponse(resp, keys)

    # get linkset data value by key
    @validate_call
    async def linksetDataGet(
        self, key: Annotated[str, Field(min_length=1)], pwd: str | None = None
    ) -> LSLResponse:
        """LSL object likset data get value by key

        returns LSLResponse.data: str
        """
        if pwd:
            resp = await self.__http.post(
                f"{self.__url}/linksetdata/read/{key}", pwd, headers=self.__headers
            )
        else:
            resp = await self.__http.get(
                f"{self.__url}/linksetdata/read/{key}", headers=self.__headers
            )
        if not await resp.text():
            raise linksetDataExceptionByNum(4, key)
        self.__log.debug(f"{key}: {await resp.text()}")
        return LSLResponse(resp, await resp.text())

    # set linkset data value
    @validate_call
    async def linksetDataWrite(
        self,
        key: Annotated[str, Field(min_length=1)],
        value: Annotated[str, Field(min_length=1)],
        pwd: str | None = None,
    ) -> LSLResponse:
        """LSL object likset data set value by key

        Arguments:
        key -   key string
        value - value string
        pwd -   optional protection password
        """
        if pwd:
            resp = await self.__http.post(
                f"{self.__url}/linksetdata/write/{key}",
                f"{value}¦{pwd}",
                headers=self.__headers,
            )
        else:
            resp = await self.__http.post(
                f"{self.__url}/linksetdata/write/{key}", value, headers=self.__headers
            )
        num = int(await resp.text())
        self.__log.debug(f"{key}: {num}")
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
        """LSL object likset data delete value by key

        Arguments:
        key -   key string
        pwd -   optional protection password
        """
        resp = await self.__http.post(
            f"{self.__url}/linksetdata/delete/{key}", pwd, headers=self.__headers
        )
        num = int(await resp.text())
        self.__log.debug(f"{key}: {num}")
        if num:
            raise linksetDataExceptionByNum(num, key)
        return LSLResponse(resp, None)

    # load inventory
    @validate_call
    async def inventoryRead(
        self, bytype: InvetoryType = InvetoryType.ANY
    ) -> LSLResponse:
        """LSL object inventory get

        Arguments:
        bytype - optional, filter InvetoryType

        returns LSLResponse.data: Invetory
        """
        items: list[InvetoryItem] = list()
        body = ["+"]

        while body[-1] == "+":
            if len(items):
                resp = await self.__http.get(
                    f"{self.__url}/inventory/read/{len(items)}?type={bytype}",
                    headers=self.__headers,
                )
            else:
                resp = await self.__http.get(
                    f"{self.__url}/inventory/read?type={bytype}", headers=self.__headers
                )
            text = await resp.text()
            body = text.split("\n")
            for line in body:
                if line != "+" and len(line):
                    args = line.split("¦")
                    items.append(
                        InvetoryItem(
                            id=args[0],
                            type=args[1],
                            name=args[2],
                            description=args[3],
                            creatorId=args[4],
                            permissions=Permissions(*args[5:10]),
                            acquireTime=args[10],
                        )
                    )

        self.__log.debug(f"{len(items)} inventory items")
        return LSLResponse(resp, Invetory(items=items, filtered=bytype))

    # delete from inventory
    @validate_call
    async def inventoryDelete(
        self, items: Annotated[Sequence[str], Field(min_length=1)]
    ):
        """LSL object inventory delete

        Arguments:
        items - Sequence[str] names
        """
        for item in items:
            if not re.match(r"^[\x20-\x7b\x7d-\x7e]{1,63}$", item):
                raise ValueError(f"'{item}' is not valid item name")

        async def dosend(body: str) -> None:
            await self.__http.post(
                f"{self.__url}/inventory/delete", body, headers=self.__headers
            )
            body = ""

        body = ""
        for item in items:
            if len(body.encode("UTF-8")) + 2 + len(item) > 2048:
                await dosend(body)
                body = ""
            if len(body):
                body += f"¦{item}"
            else:
                body = item
        if len(body):
            await dosend(body)

        self.__log.debug(f"{len(items)} deleted inventory items")

    # give inventory item
    @validate_call
    async def inventoryGive(
        self,
        destination: UUID,
        item: Annotated[str, Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{1,63}$")],
    ):
        """LSL object give item from inventory

        Arguments:
        destination - UUID avatar or object id
        item -        string item name
        """
        if not destination.int:
            raise ValueError("Can't give inventory to NULL_KEY")
        await self.__http.post(
            f"{self.__url}/inventory/give",
            f"{destination}¦{item}",
            headers=self.__headers,
        )

        self.__log.debug(f"Given to {destination} '{item}' inventory item")

    # give inventory items list
    @validate_call
    async def inventoryGiveList(
        self,
        destination: UUID,
        folder: Annotated[str, Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{1,63}$")],
        items: Annotated[Sequence[str], Field(min_length=1, max_length=41)],
    ):
        """LSL object give items from inventory

        Arguments:
        destination - UUID avatar or object id
        item -        string item name
        """
        for item in items:
            if not re.match(r"^[\x20-\x7b\x7d-\x7e]{1,63}$", item):
                raise ValueError(f"'{item}' is not valid item name")

        if not destination.int:
            raise ValueError("Can't give inventory to NULL_KEY")
        body = f'{destination}¦{folder}¦{"¦".join(items)}'
        if len(body.encode("UTF-8")) > 2048:
            raise ValueError("Too big")
        await self.__http.post(
            f"{self.__url}/inventory/givelist", body, headers=self.__headers
        )

        self.__log.debug(f"Given to {destination} '{folder}' inventory items list")
