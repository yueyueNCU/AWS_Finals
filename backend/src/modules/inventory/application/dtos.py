from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..domain.entity import ItemCategory, ItemStatus

class ExchangePartnerResponse(BaseModel):
    name: str

class ActiveExchangeResponse(BaseModel):
    exchange_id: str
    status: str
    partner: ExchangePartnerResponse

class ItemResponse(BaseModel):
    id: str
    owner_id: str
    owner_name: str
    title: str
    description: str
    category: ItemCategory
    status: ItemStatus
    image_url: Optional[str]
    created_at: datetime
    active_exchange: Optional[ActiveExchangeResponse] = Field(None, alias="activeExchange")
    
    class Config:
        populate_by_name = True # 允許使用 field name 賦值