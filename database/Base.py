from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


user_city_sm = Table(
    "user_city_sm",
    Base.metadata,
    Column("users", ForeignKey("users.telegram_id"), primary_key=True),
    Column("city_sm", ForeignKey("city_sm.city_id"), primary_key=True),
)
