import os
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

import logging

from database import Base

logging.basicConfig(level=logging.INFO)
meta = MetaData()
load_dotenv()

host = str(os.getenv("HOST_DB"))
port = str(os.getenv("PORT_DB"))
database = str(os.getenv("DB_NAME"))
user = str(os.getenv("USER"))
password = str(os.getenv("PASSWORD"))


def create_async_database() -> AsyncEngine:
    # echo параметр Тру для вывода логов, занимает время. только для дебага
    return create_async_engine(f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}", echo=False,
                               pool_recycle=1800)


async def proceed_schemas(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_session_maker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, class_=AsyncSession)
