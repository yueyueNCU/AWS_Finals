from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ItemStatus(str, Enum):
    AVAILABLE = "AVAILABLE"   # 上架中
    TRADING = "TRADING"       # 交易洽談中
    TRADED = "TRADED"         # 已交換
    HIDDEN = "HIDDEN"         # 下架 (暫時隱藏)

class ItemCategory(str, Enum):
    TEXTBOOK = "TEXTBOOK"     # 教科書
    ELECTRONICS = "3C"        # 3C 產品
    DAILY_USE = "DAILY"       # 生活用品
    FOODSTUFF = "FOOD"        # 食品
    FURNITURE = "FURNITURE"   # 家具
    OTHER = "OTHER"           # 其他

@dataclass
class ExchangePartner:
    name: str

@dataclass
class ActiveExchange:
    exchange_id: str
    status: str
    partner: ExchangePartner
    
@dataclass
class Item:
    id: str
    owner_id: str             # 刊登者 ID (關聯 User)
    title: str
    description: str
    category: ItemCategory
    status: ItemStatus
    image_url: Optional[str] = None
    created_at: datetime = datetime.now()
    owner_name: Optional[str] = None
    active_exchange: Optional[ActiveExchange] = None