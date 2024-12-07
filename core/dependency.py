from dependency_injector import containers, providers
from telebot.async_telebot import AsyncTeleBot
from config import Config

class TelegramContainer(containers.DeclarativeContainer):
    bot: AsyncTeleBot = providers.Singleton(
        AsyncTeleBot,
        Config.TG_TOKEN,
        parse_mode="HTML"
    )

tg_container = TelegramContainer()