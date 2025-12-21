from typing import List, Optional
from sqlalchemy.orm import Session
from ..domain.entity import Item, ItemCategory, ItemStatus
from ..domain.repository import ItemRepository
from .models import ItemModel
from ...iam.infrastructure.models import UserModel

class SqlAlchemyItemRepository(ItemRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, item: Item) -> Item:
        item_model = ItemModel(
            id=item.id,
            owner_id=item.owner_id,
            title=item.title,
            description=item.description,
            category=item.category,
            status=item.status,
            image_url=item.image_url,
            created_at=item.created_at
        )
        # 使用 merge 支援新增與更新
        self.db.merge(item_model)
        self.db.commit()
        return item

    def get_by_id(self, item_id: str) -> Optional[Item]:
        # 修改：加入 Join UserModel 並選取 UserModel.name
        result = self.db.query(ItemModel, UserModel.name)\
            .outerjoin(UserModel, ItemModel.owner_id == UserModel.id)\
            .filter(ItemModel.id == item_id)\
            .first()
            
        # result 會是 (ItemModel, owner_name) 的 Tuple
        return self._to_entity(result[0], result[1]) if result else None
    
    def search(self, keyword: Optional[str], category: Optional[ItemCategory]) -> List[Item]:
        # 修改：查詢時同時選取 ItemModel 和 UserModel.name
        query = self.db.query(ItemModel, UserModel.name)\
            .outerjoin(UserModel, ItemModel.owner_id == UserModel.id)\
            .filter(ItemModel.status == ItemStatus.AVAILABLE)
        
        if category:
            query = query.filter(ItemModel.category == category)
        
        if keyword:
            query = query.filter(ItemModel.title.ilike(f"%{keyword}%"))
            
        results = query.all()
        # results 是 List[(ItemModel, owner_name)]
        return [self._to_entity(row[0], row[1]) for row in results]

    def _to_entity(self, model: ItemModel, owner_name: Optional[str] = None) -> Item:
        return Item(
            id=model.id,
            owner_id=model.owner_id,
            owner_name=owner_name,
            title=model.title,
            description=model.description,
            category=ItemCategory(model.category),
            status=ItemStatus(model.status),
            image_url=model.image_url,
            created_at=model.created_at
        )