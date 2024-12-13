from telebot.formatting import hlink
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.dependency import TelegramContainer
from core.middleware import ExtendedMessage
from core.sticker_collection import TelegramStickerCollection
from db.dependency import DatabaseContainer, AsyncSession
from db.models import Users
from dependency_injector.wiring import Provide, inject

@inject
async def welcome_action(
    message: ExtendedMessage,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot],
    session: AsyncSession = Provide[DatabaseContainer.session]
):
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
            callback_data=f"registration:allow:{str(message.from_user.id)}"
        ),
        InlineKeyboardButton(
            text='❌ кто это?',
            callback_data=f"registration:deny:{str(message.from_user.id)}"
        )
     )
    for admin in admins:
        await bot.send_message(
            admin.chat_id,
            text=body,
            reply_markup=keyboard
        )

@inject
def init_module(
    bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
    bot.register_message_handler(welcome_action, commands=['start'])