from typing import List, Optional
from sqlalchemy.orm import Session, aliased
from ..domain.entity import Item, ItemCategory, ItemStatus, ActiveExchange, ExchangePartner
from ..domain.repository import ItemRepository
from .models import ItemModel
from ...iam.infrastructure.models import UserModel
from ...exchanges.infrastructure.models import ExchangeModel
from ...exchanges.domain.entity import ExchangeStatus

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
    
    def get_by_owner_id(self, owner_id: str) -> List[Item]:
        Requester = aliased(UserModel)

        # [修改] 查詢增加選取 ExchangeModel.id 和 ExchangeModel.status
        results = self.db.query(
            ItemModel, 
            UserModel.name, 
            Requester.name, 
            ExchangeModel.id, 
            ExchangeModel.status
        )\
            .outerjoin(UserModel, ItemModel.owner_id == UserModel.id)\
            .outerjoin(
                ExchangeModel, 
                (ExchangeModel.target_item_id == ItemModel.id) & 
                (ExchangeModel.status == ExchangeStatus.ACCEPTED)
            )\
            .outerjoin(Requester, ExchangeModel.requester_id == Requester.id)\
            .filter(ItemModel.owner_id == owner_id)\
            .order_by(ItemModel.created_at.desc())\
            .all()
            
        # 傳入更多的參數給 _to_entity
        return [
            self._to_entity(
                row[0], 
                owner_name=row[1], 
                partner_name=row[2], 
                exchange_id=row[3], 
                exchange_status=row[4]
            ) 
            for row in results
        ]
    
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

    def _to_entity(
        self, 
        model: ItemModel, 
        owner_name: Optional[str] = None, 
        partner_name: Optional[str] = None,
        exchange_id: Optional[str] = None,
        exchange_status: Optional[str] = None
    ) -> Item:
        
        # 組裝 ActiveExchange
        active_exchange_obj = None
        
        # [修改] 這裡多判斷 "and exchange_status"，確保它不是 None
        if partner_name and exchange_id and exchange_status:
            active_exchange_obj = ActiveExchange(
                exchange_id=exchange_id,
                status=exchange_status, # 現在 Type Checker 知道這裡一定是 str 了
                partner=ExchangePartner(name=partner_name)
            )

        return Item(
            id=model.id,
            owner_id=model.owner_id,
            owner_name=owner_name,
            title=model.title,
            description=model.description,
            category=ItemCategory(model.category),
            status=ItemStatus(model.status),
            image_url=model.image_url,
            created_at=model.created_at,
            active_exchange=active_exchange_obj
        )