from mailbox import Message

from telebot.asyncio_filters import SimpleCustomFilter
from db.models import UserRole
from core.middleware import ExtendedMessage

class IsAdmin(SimpleCustomFilter):
    key='is_admin'
    @staticmethod
    async def check(message: ExtendedMessage):
        return message.context.user_model.role == UserRole.admin

class IsUnregistered(SimpleCustomFilter):
    key='is_unregistered'
    @staticmethod
    async def check(message: ExtendedMessage):
        return message.context.user_model.role == UserRole.unregistered

class IsRegistered(SimpleCustomFilter):
    key='is_registered'
    @staticmethod
    async def check(message: ExtendedMessage):
        return message.context.user_model.role == UserRole.registered

class IsOwner(SimpleCustomFilter):
    key='is_owner'
    @staticmethod
    async def check(message: ExtendedMessage):
        return message.context.user_model.role == UserRole.owner

class IsRejected(SimpleCustomFilter):
    key='is_rejected'
    @staticmethod
    async def check(message: ExtendedMessage):
        return message.context.user_model.role == UserRole.rejected