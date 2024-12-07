from asyncio import run
from dependency_injector.wiring import inject, Provide
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from telebot import apihelper
from db.models import init_db
from core.middleware import DbMiddleware
from db.dependency import DatabaseContainer, db_container, AsyncEngine
from web.dependency import HTTPContainer, http_container
from config import Config

apihelper.ENABLE_MIDDLEWARE = True

bot = AsyncTeleBot(Config.TG_TOKEN, parse_mode="HTML")
bot.setup_middleware(DbMiddleware())

@inject
async def init(
	engine: AsyncEngine = Provide[DatabaseContainer.engine]
):
	await init_db(engine)


@bot.message_handler(commands=['start'])
async def start_message(
	message: Message,
):
	await bot.send_message(message.chat.id, 'Hello!')


async def main():
	global db_container
	db_container.init_resources()
	db_container.wire(
		modules=[
			__name__,
			'core.middleware',
			'db'
		]
	)

	http_container.init_resources()
	http_container.wire(modules=[__name__])

	await init()

	await bot.polling()


if __name__ == '__main__':
	run(main())