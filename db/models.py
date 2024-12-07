from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import select, ForeignKey, inspect

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    is_registered: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    comment: Mapped[str] = mapped_column(nullable=True)
    chat_id: Mapped[int] = mapped_column()

    @classmethod
    async def create(
        cls,
        username: str,
        first_name: str,
        last_name: str,
        chat_id: int,
        session: AsyncSession,
        comment: str = None
    ):
        user = cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            chat_id=chat_id,
            comment=comment,
        )
        session.add(user)
        await session.flush()

        return user

    @classmethod
    async def get_by_chat_id(
        cls,
        chat_id: int,
        session: AsyncSession
    ):
        query = select(cls).where(cls.chat_id == chat_id)
        return (await session.execute(query)).scalar_one_or_none()


class Messages(Base):
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    body: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)

    @classmethod
    async def create(
        cls,
        tg_id: int,
        user_id: int,
        body: str,
        session: AsyncSession,
    ):
        message = cls(
            user_id=user_id,
            body=body,
            tg_id=tg_id
        )
        session.add(message)
        await session.flush()
        return message


class DatabaseContext:
    def __init__(
        self,
        user_model: Users,
        message_model: Messages,
    ):
        self.user_model = user_model
        self.message_model = message_model


async def init_db(engine: AsyncEngine):
    async with engine.connect() as connection:
        existing_tables = await connection.run_sync(
            lambda conn: inspect(conn).get_table_names()
        )

        if "users" not in existing_tables:
            await connection.run_sync(Base.metadata.create_all)

        await connection.commit()