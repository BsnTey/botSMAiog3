from typing import TYPE_CHECKING, Optional

from database.Base import Base, user_city_sm
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

if TYPE_CHECKING:
    from database.User import User


class CitySM(Base):
    __tablename__ = "city_sm"

    city_id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    full_name: Mapped[Optional[str]]

    users: Mapped[list["User"]] = relationship(
        secondary=user_city_sm, back_populates="favourite_cities"
    )

    def __str__(self) -> str:
        return f'<CitySM {self.name}>'

    def __repr__(self) -> str:
        return str(self)
