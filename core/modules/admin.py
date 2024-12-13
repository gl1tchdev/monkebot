from telebot.types import CallbackQuery
from telebot.async_telebot import AsyncTeleBot
from core.dependency import TelegramContainer
from core.sticker_collection import TelegramStickerCollection
from db.dependency import DatabaseContainer, AsyncSession
from db.models import Users
from dependency_injector.wiring import Provide, inject


@inject
async def allow_registration(
    callback: CallbackQuery,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot],
    session: AsyncSession = Provide[DatabaseContainer.session],
):
    data = callback.data.split(':')
    user_id = int(data[2])
    user = await Users.get_by_chat_id(user_id, session)
    user.is_registered = True
    await session.commit()
    await bot.answer_callback_query(callback.id, text='Регистрация подтверждена')

    await bot.send_message(
        user_id,
        text='админ подтвердил твою принадлежность к стае'
    )
    await bot.send_sticker(
        user_id,
        sticker=TelegramStickerCollection.respect_monkey
    )

@inject
async def deny_registration(
    callback: CallbackQuery,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot],
    session: AsyncSession = Provide[DatabaseContainer.session],
):
    pass



@inject
def init_module(
    bot: AsyncTeleBot = Provide[TelegramContainer.bot],
):
    bot.register_callback_query_handler(
        allow_registration,
        func=lambda callback: True
    )