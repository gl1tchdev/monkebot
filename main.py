from asyncio import run
from dependency_injector.wiring import inject, Provide
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import TextMatchFilter, IsReplyFilter
from telebot import apihelper, logger
from db.models import init_db
from db.dependency import DatabaseContainer, db_container, AsyncEngine
from web.dependency import http_container
from core.middleware import DbModelsToMessageMiddleware
from core.filter import IsBotAdmin
from core.modules.welcome import init_module as welcome_init
from core.modules.admin import init_module as admin_init
from core.dependency import TelegramContainer, tg_container



@inject
async def startup(
	engine: AsyncEngine = Provide[DatabaseContainer.engine],
	bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
	await init_db(engine)

	apihelper.ENABLE_MIDDLEWARE = True
	bot.setup_middleware(DbModelsToMessageMiddleware())

	bot.add_custom_filter(IsReplyFilter())
	bot.add_custom_filter(TextMatchFilter())
	bot.add_custom_filter(IsBotAdmin())


	welcome_init()
	admin_init()

	await bot.polling()


async def main():
	global db_container, http_container, tg_container, wiring_list

	wiring_list = [
		__name__,
		'core.modules.welcome',
		'core.modules.admin'
	]

	db_container.init_resources()
	db_container.wire(modules=wiring_list)

	http_container.init_resources()
	http_container.wire(modules=wiring_list)

	tg_container.init_resources()
	tg_container.wire(modules=wiring_list)

	await startup()

	http_container.shutdown_resources()
	db_container.shutdown_resources()
	tg_container.shutdown_resources()


if __name__ == '__main__':
	run(main())