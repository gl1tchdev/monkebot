from aiohttp import ClientSession
from dependency_injector import containers, providers


http_session = None


class HTTPContainer(containers.DeclarativeContainer):
    client: ClientSession = providers.Singleton(ClientSession)


http_container = HTTPContainer()