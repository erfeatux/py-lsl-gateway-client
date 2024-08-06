from dependency_injector.wiring import Provide, inject

from .container import Container
from .linkset import LinkSet
from .basehttp import HTTP


class API:
    container = Container()

    def __init__(self) -> None:
        self.container.wire(modules=[__name__])

    @inject
    def linkset(self, url: str, http: HTTP = Provide[Container.http]) -> LinkSet:
        return LinkSet(http, url)
