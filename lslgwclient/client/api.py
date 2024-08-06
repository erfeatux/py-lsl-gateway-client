from dependency_injector.wiring import Provide, inject

from .container import Container
from .linkset import LinkSet


class API:
    container = Container()

    def __init__(self) -> None:
        self.container.wire(modules=[__name__])

    @inject
    def linkset(self, url: str, http: object = Provide[Container.http]) -> LinkSet:
        return LinkSet(http, url)
