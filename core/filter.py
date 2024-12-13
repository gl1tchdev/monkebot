from telebot.asyncio_filters import SimpleCustomFilter
from core.middleware import ExtendedMessage

class IsBotAdmin(SimpleCustomFilter):
    key='is_bot_admin'
    @staticmethod
    def check(message: ExtendedMessage):
        return message.context.user_model.is_admin
