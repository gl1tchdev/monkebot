from telebot.types import Message
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ForceReply
from telebot.asyncio_filters import TextFilter
from telebot.async_telebot import AsyncTeleBot
from db.models import DatabaseContext
from core.dependency import TelegramContainer
from db.dependency import DatabaseContainer, AsyncSession
from dependency_injector.wiring import Provide, inject

yes_button_text = 'оставлю комментарий'
no_button_text = 'админ и так поймет'
prompt_text = 'твой комментарий'

@inject
async def welcome_action(
    message: Message,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
    yes_button_keyboard = KeyboardButton(text=yes_button_text)
    no_button_keyboard = KeyboardButton(text=no_button_text)
    keyboard.add(yes_button_keyboard, no_button_keyboard)
    await bot.send_message(message.chat.id,
        text='бип-бип буп-буп. доступ запрещен. '
             'можешь оставить свой комментарий, чтобы было легче тебя узнать',
        reply_markup=keyboard
    )

@inject
async def welcome_yes_button(
    message: Message,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
    markup = ForceReply(selective=False)
    await bot.send_message(
        chat_id=message.chat.id,
        text=prompt_text,
        reply_markup=markup
    )

@inject
async def welcome_yes_button_get_comment(
    message: Message,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot],
    session: AsyncSession = Provide[DatabaseContainer.session]
):
    if not message.reply_to_message.any_text == prompt_text:
        return
    context: DatabaseContext = message.context
    context.user_model.comment = message.text
    await session.commit()
    await bot.send_message(message.chat.id,'направил заявку администратору')

@inject
async def welcome_no_button(
    message: Message,
    bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
    await bot.send_message(message.chat.id, 'направил заявку администратору')

async def debug(message: Message):
    print(message)


@inject
def init(
    bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
    bot.register_message_handler(welcome_action, commands=['start'])
    bot.register_message_handler(welcome_yes_button,
        text=TextFilter(equals=yes_button_text, ignore_case=True)
    )
    bot.register_message_handler(welcome_no_button,
        text=TextFilter(equals=no_button_text, ignore_case=True)
    )
    bot.register_message_handler(welcome_yes_button_get_comment, is_reply=True)
    #aabot.register_message_handler(debug, func=lambda message: True)
