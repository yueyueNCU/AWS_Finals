from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....database import get_db

# 依賴
from ...iam.dependencies import get_current_user
from ...iam.domain.entity import User
from ...inventory.infrastructure.repository import SqlAlchemyItemRepository
from ..application.dtos import (
    CreateExchangeRequest,
    ExchangeDetailResponse,
    ExchangeListResponse,
    UpdateExchangeStatusRequest,
)

# 交換模組
from ..application.service import ExchangeService
from ..infrastructure.repository import SqlAlchemyExchangeRepository

router = APIRouter(tags=["Exchanges"])


# Dependency Helper
def get_exchange_service(db: Session = Depends(get_db)) -> ExchangeService:
    exchange_repo = SqlAlchemyExchangeRepository(db)
    item_repo = SqlAlchemyItemRepository(db)
    return ExchangeService(exchange_repo, item_repo, db)


# 1. 提出交換請求
@router.post("/items/{item_id}/exchanges", status_code=201)
def create_exchange(
    item_id: str,
    request: CreateExchangeRequest,
    current_user: User = Depends(get_current_user),
    service: ExchangeService = Depends(get_exchange_service),
):
    return service.create_exchange(current_user.id, item_id, request)


# 2. 取得我的交換列表
@router.get("/exchanges", response_model=List[ExchangeListResponse])
def get_my_exchanges(
    role: str = Query(..., regex="^(requester|owner)$"),
    current_user: User = Depends(get_current_user),
    service: ExchangeService = Depends(get_exchange_service),
):
    return service.get_exchanges(current_user.id, role)


# 3. 取得單一交換詳情
@router.get("/exchanges/{exchange_id}", response_model=ExchangeDetailResponse)
def get_exchange_detail(
    exchange_id: str,
    current_user: User = Depends(get_current_user),
    service: ExchangeService = Depends(get_exchange_service),
):
    # 這裡可以加檢查是否為當事人
    detail = service.get_exchange_detail(exchange_id)
    if (
        detail["requester"]["user_id"] != current_user.id
        and detail["owner"]["user_id"] != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
    return detail


# 4. 更新交換狀態
@router.patch("/exchanges/{exchange_id}/status")
def update_exchange_status(
    exchange_id: str,
    request: UpdateExchangeStatusRequest,
    current_user: User = Depends(get_current_user),
    service: ExchangeService = Depends(get_exchange_service),
):
    return service.update_status(current_user.id, exchange_id, request)


# 5. 取消交換請求 (由提出者發起)
@router.delete("/exchanges/{exchange_id}")
def cancel_exchange(
    exchange_id: str,
    current_user: User = Depends(get_current_user),
    service: ExchangeService = Depends(get_exchange_service),
):
    return service.cancel_exchange(current_user.id, exchange_id)


# 系統資訊: 地點
@router.get("/locations")
def get_locations(service: ExchangeService = Depends(get_exchange_service)):
    return service.get_locations()


# 系統資訊: 分類 (因為 ItemCategory 是 Enum，這裡簡單回傳即可)
from ...inventory.domain.entity import ItemCategory


# @router.get("/categories")
# def get_categories():
#     # 對應前端要求的中文，這裡做個 Mapping
#     CATEGORY_MAP = {
#         ItemCategory.TEXTBOOK: "教科書",
#         ItemCategory.ELECTRONICS: "3C周邊",
#         ItemCategory.DAILY_USE: "生活用品",
#         ItemCategory.FOODSTUFF: "食品",
#         ItemCategory.FURNITURE: "家具",
#         ItemCategory.OTHER: "其他",
#     }
#     # 或者直接回傳 Enum 值讓前端翻譯，看你的需求
#     # 這裡依照你的範例回傳 List[str]
#     return list(CATEGORY_MAP.values())
