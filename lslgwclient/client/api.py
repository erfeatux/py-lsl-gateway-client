from dependency_injector.wiring import Provide, inject
from typing import Any

from .container import Container
from .linkset import LinkSet
from .basehttp import HTTP


class API:
    """lsl-gateway-client base class"""

    container = Container()

    def __init__(self) -> None:
        # wiring dependency-injector
        self.container.wire(modules=[__name__])

    @inject
    def linkset(
        self,
        url: str,
        headers: dict[str, Any] = dict(),
        http: HTTP = Provide[Container.http],
    ) -> LinkSet:
        """get LinkSet, it provides LSL object iteraction

        Arguments:
        url -     link to LSL object
        headers - optional, add headers for any request
        """
        return LinkSet(http, url, headers)
