import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ...inventory.domain.entity import ItemStatus

# 假設你需要存取 Items 來檢查擁有權或更新狀態
from ...inventory.domain.repository import ItemRepository

# 引入相關 Entity 與 Repository
from ..domain.entity import Exchange, ExchangeStatus
from ..domain.repository import ExchangeRepository

# 為了組裝回應，這裡我們可能需要直接存取 DB Model 或是使用各模組的 Repository
# 為了簡化範例，這裡假設 Service 可以存取 DB Session 做關聯查詢 (更進階做法是透過 ReadModel)
from ..infrastructure.models import ExchangeModel

# 地點清單 (暫時寫死，也可以存資料庫)
LOCATIONS = {1: "正門圓環", 2: "男九舍全家", 3: "依仁堂籃球場"}


class ExchangeService:
    def __init__(
        self, repo: ExchangeRepository, item_repo: ItemRepository, db: Session
    ):
        self.repo = repo
        self.item_repo = item_repo
        self.db = db

    def create_exchange(
        self, requester_id: str, target_item_id: str, dto: "CreateExchangeRequest"
    ) -> Exchange:
        # 1. 檢查目標物品是否存在
        target_item = self.item_repo.get_by_id(target_item_id)
        if not target_item:
            raise HTTPException(status_code=404, detail="Target item not found")

        # 檢查目標物品狀態
        if target_item.status != ItemStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail="Target item is not available")

        if target_item.owner_id == requester_id:
            raise HTTPException(status_code=400, detail="Cannot exchange with yourself")

        # 2. 如果有提供交換物，檢查是否屬於該使用者
        if dto.offered_item_id:
            offered_item = self.item_repo.get_by_id(dto.offered_item_id)
            if not offered_item or offered_item.owner_id != requester_id:
                raise HTTPException(status_code=400, detail="Invalid offered item")

            # 檢查提供物品狀態
            if offered_item.status != ItemStatus.AVAILABLE:
                raise HTTPException(
                    status_code=400, detail="Offered item is not available"
                )

        # 同一人 (requester) 對同一物 (target) 用同一交換物 (offered) 且還在 PENDING 狀態
        duplicate_query = self.db.query(ExchangeModel).filter(
            ExchangeModel.requester_id == requester_id,
            ExchangeModel.target_item_id == target_item_id,
            ExchangeModel.status == ExchangeStatus.PENDING,
        )

        # 分開處理 offered_item_id 為 None (純索取) 的狀況
        if dto.offered_item_id:
            duplicate_query = duplicate_query.filter(
                ExchangeModel.offered_item_id == dto.offered_item_id
            )
        else:
            duplicate_query = duplicate_query.filter(
                ExchangeModel.offered_item_id == None
            )

        if duplicate_query.first():
            raise HTTPException(
                status_code=400,
                detail="您已送出過相同的交換請求 (You already have a pending request with this item).",
            )

        # 3. 建立交換請求
        new_exchange = Exchange(
            id=str(uuid.uuid4()),
            requester_id=requester_id,
            owner_id=target_item.owner_id,
            target_item_id=target_item_id,
            offered_item_id=dto.offered_item_id,
            status=ExchangeStatus.PENDING,
            message=dto.message,
        )
        return self.repo.save(new_exchange)

    def get_exchanges(self, user_id: str, role: str):
        # 1. 取得原始資料
        exchanges = self.repo.find_by_user(user_id, role)

        results = []
        for e in exchanges:
            # 為了效率，這裡建議一樣做個簡單的查詢或重用 _enrich 邏輯
            # 這裡我們先用最簡單的方式：重用 _enrich 取得完整資料，再轉成前端要的格式
            full_data = self._enrich_exchange_data(e.id)

            # 2. 判斷誰是 Partner
            if role == "requester":
                # 我是申請者，Partner 就是物品主人 (owner)
                partner_info = {
                    "id": full_data["owner"]["user_id"],
                    "name": full_data["owner"]["nickname"],  # 前端用 .name
                    "avatar_url": full_data["owner"]["avatar_url"],
                }
            else:
                # 我是物品主人，Partner 就是申請者 (requester)
                partner_info = {
                    "id": full_data["requester"]["user_id"],
                    "name": full_data["requester"]["nickname"],  # 前端用 .name
                    "avatar_url": full_data["requester"]["avatar_url"],
                }

            # 3. 組裝成前端 ProfileView 預期的格式
            results.append(
                {
                    "exchange_id": full_data["id"],  # 前端要 exchange_id
                    "status": full_data["status"],
                    "partner": partner_info,  # 前端要 partner
                    "target_item": full_data["target_item"],
                    "offered_item": full_data["offered_item"],
                }
            )

        return results

    def get_exchange_detail(self, exchange_id: str) -> "ExchangeDetailResponse":
        return self._enrich_exchange_data(exchange_id)

    def update_status(
        self, user_id: str, exchange_id: str, dto: "UpdateExchangeStatusRequest"
    ):
        exchange = self.repo.get_by_id(exchange_id)
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")

        # 只有擁有者(賣家)可以接受/拒絕
        if exchange.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")

        if dto.action == "accept":
            # 再次確認物品狀態是否仍為 Available，避免並發問題
            target = self.item_repo.get_by_id(exchange.target_item_id)
            if target.status != ItemStatus.AVAILABLE:
                raise HTTPException(
                    status_code=400, detail="Item is no longer available"
                )

            exchange.status = ExchangeStatus.ACCEPTED
            exchange.meetup_location_id = dto.meetup_location_id

            # 更新物品狀態
            target.status = ItemStatus.TRADING
            self.item_repo.save(target)

            if exchange.offered_item_id:
                offered = self.item_repo.get_by_id(exchange.offered_item_id)
                # 也要檢查 offered item 是否還在
                if offered and offered.status == ItemStatus.AVAILABLE:
                    offered.status = ItemStatus.TRADING
                    self.item_repo.save(offered)
                elif offered:
                    raise HTTPException(
                        status_code=400,
                        detail="對方提供的物品已不再可用 (Offered item is no longer available)",
                    )

            # 拒絕其他人的請求
            self._reject_other_requests(exchange.target_item_id, exchange_id)

        elif dto.action == "reject":
            exchange.status = ExchangeStatus.REJECTED

        exchange.updated_at = datetime.now()
        self.repo.save(exchange)
        return self._enrich_exchange_data(exchange_id)

    def _reject_other_requests(self, target_item_id: str, current_exchange_id: str):
        """
        找出所有 target_item_id 相同，且狀態為 PENDING 的其他交換請求，
        將它們強制改為 REJECTED。
        """
        # 這裡直接使用 DB Session 進行批量更新比較快
        # 邏輯：UPDATE exchanges SET status='rejected' WHERE target_item_id=... AND id != ... AND status='pending'

        # 查詢
        others = (
            self.db.query(ExchangeModel)
            .filter(
                ExchangeModel.target_item_id == target_item_id,
                ExchangeModel.id != current_exchange_id,
                ExchangeModel.status == ExchangeStatus.PENDING,
            )
            .all()
        )

        # 更新
        for other in others:
            other.status = ExchangeStatus.REJECTED
            note = " (系統自動備註: 因物品已與他人成交，系統自動取消此請求)"
            if other.message:
                other.message += note
            else:
                other.message = note.strip()

            other.updated_at = datetime.now()
            self.db.add(other)

    def cancel_exchange(self, user_id: str, exchange_id: str):
        exchange = self.repo.get_by_id(exchange_id)
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")

        # 驗證權限：只有「提出者 (Requester)」可以取消
        if exchange.requester_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")

        # 驗證狀態：只有 PENDING (等待中) 的請求可以取消
        # 如果對方已經接受了，就不能隨便取消 (可能需要聊聊協調)
        if exchange.status != ExchangeStatus.PENDING:
            raise HTTPException(
                status_code=400, detail="Only pending requests can be cancelled"
            )

        # 更新狀態為 CANCELLED
        exchange.status = ExchangeStatus.CANCELLED
        exchange.updated_at = datetime.now()
        self.repo.save(exchange)

        return self._enrich_exchange_data(exchange_id)

    def _enrich_exchange_data(self, exchange_id: str):
        # 使用 SQLAlchemy Model 直接做 Join 查詢以取得 User 和 Item 資料
        # 這樣比一個個用 Repository 查更有效率
        model = (
            self.db.query(ExchangeModel).filter(ExchangeModel.id == exchange_id).first()
        )
        if not model:
            raise HTTPException(status_code=404, detail="Exchange not found")

        # 組裝回應
        deal_info = None
        if (
            model.status in [ExchangeStatus.ACCEPTED, ExchangeStatus.COMPLETED]
            and model.meetup_location_id
        ):
            loc_name = LOCATIONS.get(model.meetup_location_id, "Unknown")
            deal_info = {
                "meetup_location": {"id": model.meetup_location_id, "name": loc_name},
                "accepted_at": model.updated_at,  # 簡化：用更新時間當作接受時間
            }

        return {
            "id": model.id,
            "status": model.status,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
            "message": model.message,
            "requester": {
                "user_id": model.requester.id,
                "nickname": model.requester.name,  # 對應 UserModel.name
                "avatar_url": model.requester.avatar_url,
            },
            "owner": {
                "user_id": model.owner.id,
                "nickname": model.owner.name,
                "avatar_url": model.owner.avatar_url,
            },
            "target_item": {
                "item_id": model.target_item.id,
                "title": model.target_item.title,
                "cover_image": model.target_item.image_url,
                "status": model.target_item.status,
            },
            "offered_item": (
                {
                    "item_id": model.offered_item.id,
                    "title": model.offered_item.title,
                    "cover_image": model.offered_item.image_url,
                }
                if model.offered_item
                else None
            ),
            "deal_info": deal_info,
        }

    def get_locations(self):
        return [{"id": k, "name": v} for k, v in LOCATIONS.items()]
