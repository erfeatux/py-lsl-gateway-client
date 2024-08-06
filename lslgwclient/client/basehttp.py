# this module contains the http request mechanism
# fake for unit tests

import abc
from uuid import uuid4

creatorId = uuid4()


class ClientResponse(abc.ABC):
    headers: dict[str, str]

    @abc.abstractmethod
    def __init__(self, text: str) -> None:
        pass

    @abc.abstractmethod
    async def text(self) -> str:
        pass


class HTTP:
    # http get method
    @staticmethod
    @abc.abstractmethod
    async def get(url: str) -> ClientResponse:
        pass

    # http get method
    @staticmethod
    @abc.abstractmethod
    async def post(url: str, data: str | None) -> ClientResponse:
        pass
