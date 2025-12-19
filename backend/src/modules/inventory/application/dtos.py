from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..domain.entity import ItemCategory, ItemStatus

class ItemCreateRequest(BaseModel):
    title: str
    description: str
    category: ItemCategory
class ItemResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    description: str
    category: ItemCategory
    status: ItemStatus
    image_url: Optional[str]
    created_at: datetime