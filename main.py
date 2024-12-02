from asyncio import run
from os.path import exists
from dependency_injector.wiring import inject, Provide
from telebot.async_telebot import AsyncTeleBot
from sqlalchemy.ext.asyncio import AsyncSession
from telebot.types import Message
from db.models import init_tables, User
from db.dependency import DatabaseContainer, db_container, AsyncEngine
from web.dependency import HTTPContainer, http_container
from config import Config


bot = AsyncTeleBot(Config.TG_TOKEN, parse_mode="HTML")

@inject
async def init(
	engine: AsyncEngine = Provide[DatabaseContainer.engine],
	session: AsyncSession = Provide[DatabaseContainer.session],
):
	if exists('telegram.db'):
		return

	await init_tables(engine, session)


@bot.message_handler(commands=['start'])
@inject
async def start_message(
	message: Message,
	session: AsyncSession = Provide[DatabaseContainer.session],
):
	await bot.send_message(message.chat.id, 'Hello!')
	async with session:
		if not (await User.exists(message.from_user.username, session)):
			await User.create(message.from_user.username, session)
		await session.commit()


async def main():
	db_container.init_resources()
	db_container.wire(modules=[__name__])

	http_container.init_resources()
	http_container.wire(modules=[__name__])

	await init()

	await bot.polling(restart_on_change=True)


if __name__ == '__main__':
	run(main())