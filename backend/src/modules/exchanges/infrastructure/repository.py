from typing import List, Optional

from sqlalchemy.orm import Session

from ..domain.entity import Exchange, ExchangeStatus
from ..domain.repository import ExchangeRepository
from .models import ExchangeModel


class SqlAlchemyExchangeRepository(ExchangeRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, exchange: Exchange) -> Exchange:
        model = ExchangeModel(
            id=exchange.id,
            requester_id=exchange.requester_id,
            owner_id=exchange.owner_id,
            target_item_id=exchange.target_item_id,
            offered_item_id=exchange.offered_item_id,
            status=exchange.status,
            message=exchange.message,
            meetup_location_id=exchange.meetup_location_id,
            requester_confirmed=exchange.requester_confirmed,
            owner_confirmed=exchange.owner_confirmed,
            created_at=exchange.created_at,
            updated_at=exchange.updated_at,
        )
        self.db.merge(model)
        self.db.commit()
        return exchange

    def get_by_id(self, exchange_id: str) -> Optional[Exchange]:
        model = (
            self.db.query(ExchangeModel).filter(ExchangeModel.id == exchange_id).first()
        )
        return self._to_entity(model) if model else None

    def find_by_user(self, user_id: str, role: str) -> List[Exchange]:
        query = self.db.query(ExchangeModel)
        if role == "requester":
            query = query.filter(ExchangeModel.requester_id == user_id)
        elif role == "owner":
            query = query.filter(ExchangeModel.owner_id == user_id)

        # 依時間倒序
        models = query.order_by(ExchangeModel.created_at.desc()).all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: ExchangeModel) -> Exchange:
        return Exchange(
            id=model.id,
            requester_id=model.requester_id,
            owner_id=model.owner_id,
            target_item_id=model.target_item_id,
            offered_item_id=model.offered_item_id,
            status=ExchangeStatus(model.status),
            message=model.message,
            meetup_location_id=model.meetup_location_id,
            requester_confirmed=model.requester_confirmed,
            owner_confirmed=model.owner_confirmed,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
