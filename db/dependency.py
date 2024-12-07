from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import Config

class DatabaseContainer(containers.DeclarativeContainer):
    engine: providers.Singleton[AsyncEngine] = providers.Singleton(
        create_async_engine,
        url=Config.PG_DSN
    )
    session_factory: providers.Factory[sessionmaker] = providers.Factory(
        sessionmaker,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session: providers.Resource[AsyncSession] = providers.Resource(
        lambda session_factory: session_factory(),
        session_factory=session_factory,
    )

db_container = DatabaseContainer()