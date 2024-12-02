from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import select

class Base(DeclarativeBase):
    pass

async def init_tables(
    engine: AsyncEngine,
    session: AsyncSession,
) -> None:
    meta = Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    user = User(username='gl1tch4', is_admin=True)
    session.add(user)
    await session.commit()


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    comment: Mapped[str] = mapped_column(nullable=True)

    @classmethod
    async def create(
        cls,
        username: str,
        session: AsyncSession
    ):
        user = cls(username=username)
        session.add(user)
        await session.flush()

        return user

    @classmethod
    async def exists(
        cls,
        username: str,
        session: AsyncSession
    ) -> bool:
        result = select(cls).where(cls.username == username)

        return (await session.execute(result)) is not None
