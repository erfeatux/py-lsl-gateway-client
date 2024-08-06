from dependency_injector import containers, providers

from .http import HTTP


class Container(containers.DeclarativeContainer):
    http = providers.Singleton(HTTP)
