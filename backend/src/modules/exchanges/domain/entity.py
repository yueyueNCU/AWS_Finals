from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


# 定義交換狀態
class ExchangeStatus(str, Enum):
    PENDING = "pending"  # 等待賣家回應
    ACCEPTED = "accepted"  # 賣家已接受，準備面交
    REJECTED = "rejected"  # 賣家拒絕
    COMPLETED = "completed"  # 雙方確認完成
    CANCELLED = "cancelled"  # 取消


@dataclass
class Exchange:
    id: str
    requester_id: str  # 提出交換的人
    owner_id: str  # 物品擁有者 (被請求者)
    target_item_id: str  # 對方的物品 ID
    offered_item_id: Optional[str]  # 我提供的物品 ID (可為 Null)
    status: ExchangeStatus
    message: Optional[str] = None
    meetup_location_id: Optional[int] = None
    requester_confirmed: bool = False
    owner_confirmed: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
