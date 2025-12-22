from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from ..domain.entity import ExchangeStatus


# Request DTOs
class CreateExchangeRequest(BaseModel):
    offered_item_id: Optional[str] = None
    message: str


class UpdateExchangeStatusRequest(BaseModel):
    action: str  # "accept" or "reject"
    meetup_location_id: Optional[int] = None


# Response DTOs (Nested Structures)
class UserInfo(BaseModel):
    user_id: str
    nickname: str
    avatar_url: Optional[str]


class ItemInfo(BaseModel):
    item_id: str
    title: str
    cover_image: Optional[str] = None
    status: Optional[str] = None


class LocationInfo(BaseModel):
    id: int
    name: str


class DealInfo(BaseModel):
    meetup_location: Optional[LocationInfo]
    accepted_at: Optional[datetime]


class ExchangeListPartner(BaseModel):
    id: str
    name: str
    avatar_url: Optional[str] = None


class ExchangeListItem(BaseModel):
    title: str
    # 如果前端需要圖片或其他資訊，也可以加在這裡


class ExchangeListResponse(BaseModel):
    exchange_id: str
    status: ExchangeStatus
    partner: ExchangeListPartner
    target_item: ExchangeListItem
    offered_item: Optional[ExchangeListItem] = None


class ExchangeDetailResponse(BaseModel):
    id: str
    status: ExchangeStatus
    created_at: datetime
    updated_at: datetime
    requester: UserInfo
    owner: UserInfo
    target_item: ItemInfo
    offered_item: Optional[ItemInfo]
    deal_info: Optional[DealInfo]
    message: Optional[str]


class SendMessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    sender_id: str
    sender_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateLocationRequest(BaseModel):
    meetup_location_id: int


class ConfirmExchangeRequest(BaseModel):
    pass
