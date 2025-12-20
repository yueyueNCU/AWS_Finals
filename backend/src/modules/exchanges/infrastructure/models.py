from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...iam.infrastructure.models import Base, UserModel
from ...inventory.infrastructure.models import ItemModel
from ..domain.entity import ExchangeStatus


class ExchangeModel(Base):
    __tablename__ = "exchanges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    requester_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )

    target_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("items.id"))
    offered_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id"), nullable=True
    )

    status: Mapped[str] = mapped_column(
        SAEnum(ExchangeStatus), default=ExchangeStatus.PENDING
    )
    message: Mapped[str] = mapped_column(Text, nullable=True)
    meetup_location_id: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # 建立關聯以便撈取詳細資料 (Optional, 但建議加上方便 Join)
    requester = relationship("UserModel", foreign_keys=[requester_id])
    owner = relationship("UserModel", foreign_keys=[owner_id])
    target_item = relationship("ItemModel", foreign_keys=[target_item_id])
    offered_item = relationship("ItemModel", foreign_keys=[offered_item_id])
