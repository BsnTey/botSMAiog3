from typing import TYPE_CHECKING
from typing import Optional
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from database.Base import Base, user_city_sm

if TYPE_CHECKING:
    from database.Account import Account
    from database.CitySM import CitySM


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[str] = mapped_column(primary_key=True, unique=True)
    telegram_name: Mapped[str]
    first_name: Mapped[Optional[str]]
    login: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]
    count_bonuses: Mapped[int] = mapped_column(default=0)
    is_ban: Mapped[bool] = mapped_column(default=False)

    accounts: Mapped[list["Account"]] = relationship(back_populates="owner")

    favourite_cities: Mapped[list["CitySM"]] = relationship(
        secondary=user_city_sm, back_populates="users"
    )


    def __str__(self) -> str:
        return f'<User:{self.telegram_id}, {self.telegram_name}, {self.login}>'

    def __repr__(self) -> str:
        return str(self)
