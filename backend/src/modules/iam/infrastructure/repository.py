from typing import Optional
from sqlalchemy.orm import Session
from ..domain.entity import User
from ..domain.repository import UserRepository
from .models import UserModel

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        # 1. 把 Domain Entity 轉成 SQL Model
        user_model = UserModel(
            id=user.id,
            email=user.email,
            name=user.name,
            password_hash=user.password_hash,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            is_admin=user.is_admin
        )

        # 2. 使用 merge (如果 ID 存在就更新，不存在就新增)
        # 這比 add() 更安全，適合 "Save" 的語意
        merged_model = self.db.merge(user_model)
        self.db.commit()
        # 如果需要回傳最新狀態，建議從 merged_model 轉回 Entity
        # return self._to_entity(merged_model) 
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        # 執行 SQL 查詢
        user_model = self.db.query(UserModel).filter(UserModel.email == email).first()
        
        if user_model:
            return self._to_entity(user_model)
        return None

    def get_by_id(self, user_id: str) -> Optional[User]:
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if user_model:
            return self._to_entity(user_model)
        return None

    # --- 私有輔助方法：Mapper ---
    # 把 "骯髒" 的 SQL Model 轉回 "乾淨" 的 Domain Entity
    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            name=model.name,
            password_hash=model.password_hash,
            avatar_url=model.avatar_url,
            is_active=model.is_active,
            is_admin=model.is_admin
        )