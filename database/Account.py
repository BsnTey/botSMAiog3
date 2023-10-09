from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey

from database.Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from database.User import User
    from database.AccountOrder import AccountOrder


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[str] = mapped_column(primary_key=True)

    email: Mapped[str]
    pass_imap: Mapped[str]
    pass_email: Mapped[str]
    cookie: Mapped[str]
    access_token: Mapped[str]
    refresh_token: Mapped[str]
    x_user_id: Mapped[str]
    device_id: Mapped[str]
    installation_id: Mapped[str]

    expires_in: Mapped[int]

    is_access_mp: Mapped[bool] = mapped_column(default=False)
    is_access_cookie: Mapped[bool] = mapped_column(default=False)
    is_only_access_order: Mapped[bool] = mapped_column(default=False)

    bonus_count: Mapped[str] = mapped_column(default=False)
    is_update_bonus: Mapped[bool] = mapped_column(default=False)

    # owner_id = Column(String, ForeignKey("users.telegram_id"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.telegram_id"))
    owner: Mapped["User"] = relationship(back_populates="accounts")

    # account_orders = relationship("AccountOrder", back_populates="account")
    account_orders: Mapped["AccountOrder"] = relationship(back_populates="account")

    def __str__(self) -> str:
        return f'<Account {self.account_id}>'

    def __repr__(self) -> str:
        return str(self)


