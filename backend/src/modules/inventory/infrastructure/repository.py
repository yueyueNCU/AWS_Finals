from typing import List, Optional
from sqlalchemy.orm import Session
from ..domain.entity import Item, ItemCategory, ItemStatus
from ..domain.repository import ItemRepository
from .models import ItemModel

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
        model = self.db.query(ItemModel).filter(ItemModel.id == item_id).first()
        return self._to_entity(model) if model else None

    def search(self, keyword: Optional[str], category: Optional[ItemCategory]) -> List[Item]:
        query = self.db.query(ItemModel).filter(ItemModel.status == ItemStatus.AVAILABLE)
        
        if category:
            query = query.filter(ItemModel.category == category)
        
        if keyword:
            # 簡單的模糊搜尋
            query = query.filter(ItemModel.title.ilike(f"%{keyword}%"))
            
        models = query.all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: ItemModel) -> Item:
        return Item(
            id=model.id,
            owner_id=model.owner_id,
            title=model.title,
            description=model.description,
            category=ItemCategory(model.category),
            status=ItemStatus(model.status),
            image_url=model.image_url,
            created_at=model.created_at
        )