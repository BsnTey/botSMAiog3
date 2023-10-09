import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database import get_session_maker, create_async_database



token = str(os.getenv("BOT_TOKEN"))


bot = Bot(token=token, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
async_engine = create_async_database()
session_db = get_session_maker(async_engine)