from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from ...iam.infrastructure.models import Base  # 重用同一個 Base
from ..domain.entity import ItemStatus, ItemCategory

class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    owner_id: Mapped[str] = mapped_column(String, index=True) # 誰刊登的
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    
    # 儲存 Enum 為字串
    category: Mapped[str] = mapped_column(SAEnum(ItemCategory))
    status: Mapped[str] = mapped_column(SAEnum(ItemStatus), default=ItemStatus.AVAILABLE)
    
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)