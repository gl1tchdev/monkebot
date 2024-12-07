from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.types import Message
from dependency_injector.wiring import Provide, inject
from db.dependency import DatabaseContainer
from db.models import AsyncSession, Users, Messages, DatabaseContext


class DbMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message']

    @inject
    async def pre_process(
        self,
        message: Message,
        data,
        session: AsyncSession = Provide[DatabaseContainer.session],
    ) -> None:
        db_user = await Users.get_by_chat_id(message.chat.id, session)
        if not db_user:
            db_user = await Users.create(
                username=message.chat.username,
                first_name=message.chat.first_name,
                last_name=message.chat.last_name,
                chat_id=message.chat.id,
                session=session
            )
        db_message = await Messages.create(
            user_id=db_user.id,
            body=message.text,
            tg_id=message.id,
            session=session
        )
        await session.commit()

        context = DatabaseContext(db_user, db_message)

        message.context = context

    async def post_process(self, message, data, exception):
        pass
