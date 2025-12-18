from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

# 這是 SQLAlchemy 的基底類別
Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"

    # 這裡的定義要盡量對應 Domain Entity，但允許有資料庫特有的設定 (如 index)
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)