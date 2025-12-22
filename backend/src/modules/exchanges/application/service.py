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
from ..infrastructure.models import ExchangeModel, MessageModel
from .dtos import (
    CreateExchangeRequest,
    ExchangeDetailResponse,
    UpdateExchangeStatusRequest,
)

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

        if exchange.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")

        if dto.action == "accept":
            # --- [Step 1] 先做所有檢查 (Check Phase) ---

            # 1. 檢查我的物品 (Target)
            target = self.item_repo.get_by_id(exchange.target_item_id)
            if target.status != ItemStatus.AVAILABLE:
                raise HTTPException(
                    status_code=400, detail="Item is no longer available"
                )

            # 2. 檢查對方的物品 (Offered) - 這裡只檢查，先不存檔
            offered = None
            if exchange.offered_item_id:
                offered = self.item_repo.get_by_id(exchange.offered_item_id)
                # 若找不到物品或狀態不對，直接報錯，這時還沒修改 target，所以很安全
                if offered and offered.status != ItemStatus.AVAILABLE:
                    raise HTTPException(
                        status_code=400,
                        detail="對方提供的物品已不再可用 (Offered item is no longer available)",
                    )

            # --- [Step 2] 檢查全部通過，才執行狀態更新 (Update Phase) ---

            # 更新 Exchange
            exchange.status = ExchangeStatus.ACCEPTED
            exchange.meetup_location_id = dto.meetup_location_id

            # 更新 Target Item
            target.status = ItemStatus.TRADING
            self.item_repo.save(target)

            # 更新 Offered Item (如果有)
            if offered:
                offered.status = ItemStatus.TRADING
                self.item_repo.save(offered)
                self._reject_related_requests_for_offered_item(
                    exchange.offered_item_id, exchange_id
                )

            # 拒絕其他請求
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
        exchange_model = (
            self.db.query(ExchangeModel).filter(ExchangeModel.id == exchange_id).first()
        )
        if not exchange_model:
            raise HTTPException(status_code=404, detail="Exchange not found")

        if user_id not in [exchange_model.requester_id, exchange_model.owner_id]:
            raise HTTPException(status_code=403, detail="Permission denied")

        # 允許 PENDING 或 ACCEPTED 狀態取消
        if exchange_model.status not in [
            ExchangeStatus.PENDING,
            ExchangeStatus.ACCEPTED,
        ]:
            raise HTTPException(
                status_code=400, detail="Cannot cancel completed or rejected exchanges"
            )

        # 如果是 ACCEPTED (交易中) 狀態取消，需要還原物品狀態
        if exchange_model.status == ExchangeStatus.ACCEPTED:
            # 還原 target item
            target = self.item_repo.get_by_id(exchange_model.target_item_id)
            if target:
                target.status = ItemStatus.AVAILABLE
                self.db.add(target)

            # 還原 offered item (如果有)
            if exchange_model.offered_item_id:
                offered = self.item_repo.get_by_id(exchange_model.offered_item_id)
                if offered:
                    offered.status = ItemStatus.AVAILABLE
                    self.db.add(offered)

        # 更新狀態
        exchange_model.status = ExchangeStatus.CANCELLED
        exchange_model.updated_at = datetime.now()
        self.db.commit()

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
            "requester_confirmed": model.requester_confirmed,
            "owner_confirmed": model.owner_confirmed,
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

    def _reject_related_requests_for_offered_item(
        self, offered_item_id: str, current_exchange_id: str
    ):
        """
        當提供的物品被交易後，將其他所有使用該物品作為 offered_item 的請求，
        以及所有以該物品為 target_item 的請求 (如果有的話) 全部拒絕。
        """
        # 情況 1: 找出其他 "我拿這個物品去換別人東西" 的請求 (User Case)
        # 條件: offered_item_id 相同 AND id != current AND status = PENDING
        outgoing_conflicts = (
            self.db.query(ExchangeModel)
            .filter(
                ExchangeModel.offered_item_id == offered_item_id,
                ExchangeModel.id != current_exchange_id,
                ExchangeModel.status == ExchangeStatus.PENDING,
            )
            .all()
        )

        # 情況 2: 找出 "別人想要換我這個物品" 的請求
        # 條件: target_item_id 相同 AND status = PENDING
        # (因為這個物品已經拿去換別人的東西了，所以別人不能再來換它)
        incoming_conflicts = (
            self.db.query(ExchangeModel)
            .filter(
                ExchangeModel.target_item_id == offered_item_id,
                # 這裡不需要排除 current_exchange_id，因為 current 的 target 是對方的物品
                ExchangeModel.status == ExchangeStatus.PENDING,
            )
            .all()
        )

        all_conflicts = outgoing_conflicts + incoming_conflicts

        for conflict in all_conflicts:
            conflict.status = ExchangeStatus.REJECTED
            note = " (系統自動備註: 因交換物品已用於其他交易，系統自動取消此請求)"
            if conflict.message:
                conflict.message += note
            else:
                conflict.message = note.strip()

            conflict.updated_at = datetime.now()
            self.db.add(conflict)

    def get_locations(self):
        return [{"id": k, "name": v} for k, v in LOCATIONS.items()]

    def send_message(self, user_id: str, exchange_id: str, content: str):
        exchange = self.repo.get_by_id(exchange_id)
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")

        # 驗證使用者是否為交換雙方之一
        if user_id not in [exchange.requester_id, exchange.owner_id]:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 建立訊息
        new_msg = MessageModel(
            exchange_id=exchange_id, sender_id=user_id, content=content
        )
        self.db.add(new_msg)
        self.db.commit()
        self.db.refresh(new_msg)
        return new_msg

    def get_messages(self, user_id: str, exchange_id: str):
        # 驗證權限
        exchange = self.repo.get_by_id(exchange_id)
        if not exchange or user_id not in [exchange.requester_id, exchange.owner_id]:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 查詢訊息 (依時間排序)
        messages = (
            self.db.query(MessageModel)
            .filter(MessageModel.exchange_id == exchange_id)
            .order_by(MessageModel.created_at.asc())
            .all()
        )

        # 轉換格式 (包含 sender_name 方便前端顯示)
        results = []
        for msg in messages:
            sender_name = msg.sender.name if msg.sender else "Unknown"
            results.append(
                {
                    "id": msg.id,
                    "sender_id": msg.sender_id,
                    "sender_name": sender_name,
                    "content": msg.content,
                    "created_at": msg.created_at,
                }
            )
        return results

    # --- [新功能 2] 雙方確認完成 ---
    def confirm_exchange(self, user_id: str, exchange_id: str):
        # 使用 DB Model 比較方便直接修改 Boolean 欄位
        exchange_model = (
            self.db.query(ExchangeModel).filter(ExchangeModel.id == exchange_id).first()
        )
        if not exchange_model:
            raise HTTPException(status_code=404, detail="Exchange not found")

        if exchange_model.status != ExchangeStatus.ACCEPTED:
            raise HTTPException(
                status_code=400, detail="Exchange is not in trading status"
            )

        # 更新確認旗標
        if user_id == exchange_model.requester_id:
            exchange_model.requester_confirmed = True
        elif user_id == exchange_model.owner_id:
            exchange_model.owner_confirmed = True
        else:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 檢查是否雙方都已確認
        if exchange_model.requester_confirmed and exchange_model.owner_confirmed:
            exchange_model.status = ExchangeStatus.COMPLETED

            # TODO: 更新物品狀態為 "SOLD" 或 "COMPLETED" (視你的 ItemStatus 定義而定)
            # self._mark_items_as_sold(exchange_model.target_item_id, exchange_model.offered_item_id)

        exchange_model.updated_at = datetime.now()
        self.db.commit()

        return self._enrich_exchange_data(exchange_id)
