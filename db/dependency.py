from config import Config

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


class DatabaseContainer(containers.DeclarativeContainer):
    engine: AsyncEngine = providers.Singleton(
        create_async_engine,
        Config.SQLITE_DSN
    )
    session_maker: async_sessionmaker = providers.Factory(
        async_sessionmaker,
        bind=engine,
        expire_on_commit=False
    )

    session = providers.Resource(
        lambda session_maker: session_maker(),
        session_maker=session_maker
    )


db_container = DatabaseContainer()