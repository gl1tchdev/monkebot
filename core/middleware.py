from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.types import Message
from dependency_injector.wiring import Provide, inject
from db.dependency import DatabaseContainer
from db.models import AsyncSession, Users, Messages, MessageDbContext


class ExtendedMessage(Message):
    context: MessageDbContext

class DbModelsToMessageMiddleware(BaseMiddleware):
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
                full_name=message.from_user.full_name,
                chat_id=message.chat.id,
                session=session
            )

        args = [db_user]
        if message.text is not None:
            db_message = await Messages.create(
                user_id=db_user.id,
                body=message.text,
                tg_id=message.id,
                session=session
            )
            args.append(db_message)
        message.context = MessageDbContext(*args)
        await session.commit()

    async def post_process(self, message, data, exception):
        pass
