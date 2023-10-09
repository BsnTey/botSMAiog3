from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.Base import Base

if TYPE_CHECKING:
    from database.Account import Account

class AccountOrder(Base):
    __tablename__ = "account_orders"

    id: Mapped[str] = mapped_column(primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id"))
    order_number: Mapped[str]
    order_info: Mapped[str]

    # account = relationship("Account", back_populates="account_orders")
    account: Mapped["Account"] = relationship(back_populates="account_orders")

    def __str__(self) -> str:
        return f'<AccountOrder {self.id}>'

    def __repr__(self) -> str:
        return str(self)
