from telebot.types import CallbackQuery
from telebot.async_telebot import AsyncTeleBot
from core.dependency import TelegramContainer
from core.sticker_collection import TelegramStickerCollection
from db.dependency import DatabaseContainer, AsyncSession
from db.models import Users, UserRole, RegisterRequests, RegisterStatus
from dependency_injector.wiring import Provide, inject


@inject
async def approve_registration(
    callback: CallbackQuery,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot],
    session: AsyncSession = Provide[DatabaseContainer.session],
):
    data = callback.data.split(':')
    register_request_id = int(data[2])
    register_request = await RegisterRequests.get_by_id(register_request_id, session)
    user = await Users.get_by_id(register_request.user_id, session)

    if register_request.status != RegisterStatus.pending:
        await bot.delete_message(callback.message.chat.id, callback.message.id)
        await bot.answer_callback_query(callback.id, 'ты опоздал')
        return

    user.role = UserRole.registered
    register_request.status = RegisterStatus.approved

    await session.commit()
    await bot.answer_callback_query(callback.id, text='регистрация монке подтверждена')
    await bot.delete_message(callback.message.chat.id, callback.message.id)

    await bot.send_message(
        user.chat_id,
        text='админ подтвердил твою принадлежность к стае'
    )
    await bot.send_sticker(
        user.chat_id,
        sticker=TelegramStickerCollection.respect_monkey
    )

@inject
async def reject_registration(
    callback: CallbackQuery,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot],
    session: AsyncSession = Provide[DatabaseContainer.session],
):
    data = callback.data.split(':')
    register_request_id = int(data[2])
    register_request = await RegisterRequests.get_by_id(register_request_id, session)
    user = await Users.get_by_id(register_request.user_id, session)

    if register_request.status != RegisterStatus.pending:
        await bot.delete_message(callback.message.chat.id, callback.message.id)
        await bot.answer_callback_query(callback.id, 'ты опоздал')
        return

    user.role = UserRole.rejected
    register_request.status = RegisterStatus.rejected
    await session.commit()

    await bot.answer_callback_query(callback.id, text='туда его')
    await bot.delete_message(callback.message.chat.id, callback.message.id)


    await bot.send_message(
        user.chat_id,
        text='админ тебя не знает'
    )

@inject
def init_module(
    bot: AsyncTeleBot = Provide[TelegramContainer.bot],
):
    bot.register_callback_query_handler(
        approve_registration,
        func=lambda callback: callback.data.startswith('registration:approve'),
    )
    bot.register_callback_query_handler(
        reject_registration,
        func=lambda callback: callback.data.startswith('registration:reject'),
    )