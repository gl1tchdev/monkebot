from telebot.custom_filters import SimpleCustomFilter
from telebot.types import Message

class IsAdmin(SimpleCustomFilter):
    key='is_admin'
    @staticmethod
    def check(message: Message):
        pass
