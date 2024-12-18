from asyncio import run
from dependency_injector.wiring import inject, Provide
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import TextMatchFilter, IsReplyFilter
from telebot import apihelper
from db.models import init_db
from db.dependency import DatabaseContainer, db_container, AsyncEngine
from core.middleware import DbModelsToMessageMiddleware
from core.filters.role import IsAdmin, IsOwner, IsRegistered, IsUnregistered, IsRejected
from core.modules.register import init_module as welcome_init
from core.modules.register_callback import init_module as register_callback_init
from core.dependency import TelegramContainer, tg_container
from web.dependency import http_container, HTTPContainer


@inject
async def startup(
	engine: AsyncEngine = Provide[DatabaseContainer.engine],
	bot: AsyncTeleBot = Provide[TelegramContainer.bot]
):
	await init_db(engine)

	apihelper.ENABLE_MIDDLEWARE = True
	apihelper.SESSION_TIME_TO_LIVE = 5 * 60

	bot.setup_middleware(DbModelsToMessageMiddleware())

	bot.add_custom_filter(IsReplyFilter())
	bot.add_custom_filter(TextMatchFilter())

	bot.add_custom_filter(IsAdmin())
	bot.add_custom_filter(IsOwner())
	bot.add_custom_filter(IsRegistered())
	bot.add_custom_filter(IsUnregistered())
	bot.add_custom_filter(IsRejected())



	welcome_init()
	register_callback_init()

	await bot.infinity_polling()


async def main():
	global db_container, http_container, tg_container, wiring_list

	wiring_list = [
		__name__,
		'core.modules.register',
		'core.modules.register_callback'
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