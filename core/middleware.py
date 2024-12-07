from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.types import Message
from dependency_injector.wiring import Provide, inject

from db.dependency import DatabaseContainer
from db.models import AsyncSession, Users, Messages

class AsyncProvide(Provide):
    async def __call__(self):
        return self

class DbMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message']

    async def pre_process(self, message, data):
        pass


    @inject
    async def post_process(
        self,
        message: Message,
        data,
        exception,
        session: AsyncSession = Provide[DatabaseContainer.session]
    ):
        user = await Users.get_by_chat_id(message.chat.id, session)
        if not user:
            user = await Users.create(
                username=message.chat.username,
                chat_id=message.chat.id,
                session=session
            )
        await Messages.create(
            user_id=user.id,
            body=message.text,
            tg_id=message.id,
            session=session
        )
        await session.commit()

