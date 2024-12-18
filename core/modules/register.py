from telebot.formatting import hlink
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.dependency import TelegramContainer
from core.middleware import ExtendedMessage
from core.sticker_collection import TelegramStickerCollection
from db.dependency import DatabaseContainer, AsyncSession
from db.models import Users, RegisterRequests
from dependency_injector.wiring import Provide, inject


@inject
async def start(
    message: ExtendedMessage,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
    await bot.send_message(message.chat.id, 'тапни для регистрации: /register')

@inject
async def reject(
    message: ExtendedMessage,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
    await bot.send_sticker(message.chat.id, TelegramStickerCollection.running_monkey)
    await bot.send_message(
        message.chat.id,
        'о нет, ты не монке. админ разбанит если передумает'
    )

@inject
async def register(
    message: ExtendedMessage,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot],
    session: AsyncSession = Provide[DatabaseContainer.session]
):
    request_exists = await RegisterRequests.exists_pending(message.context.user_model.id, session)
    if request_exists:
        await bot.send_message(message.chat.id, 'заявка в процессе')
        return

    register_request = await RegisterRequests.create(
        user_id=message.context.user_model.id,
        session=session
    )

    await bot.send_message(
        message.chat.id,
        text='бегу сообщать админу о твоем появлении. доступ к функционалу появится после одобрения заявки',
    )
    await bot.send_sticker(
        message.chat.id,
        sticker=TelegramStickerCollection.running_monkey_2
    )
    admins = await Users.get_admins(session)

    user_link = f't.me/{message.from_user.username}'
    body =  f"{hlink(content=message.from_user.full_name, url=user_link)} просит впустить"

    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            text='✅ добро',
            callback_data=f"registration:approve:{register_request.id}"
        ),
        InlineKeyboardButton(
            text='❌ кто это?',
            callback_data=f"registration:reject:{register_request.id}"
        )
     )
    for admin in admins:
        await bot.send_message(
            admin.chat_id,
            text=body,
            reply_markup=keyboard
        )

    await session.commit()

@inject
def init_module(
    bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
    bot.register_message_handler(start, commands=['start'], is_unregistered=True)
    bot.register_message_handler(register, commands=['register'], is_unregistered=True)
    bot.register_message_handler(reject, is_rejected=True)