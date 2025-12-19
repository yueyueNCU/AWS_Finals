import uuid
from datetime import datetime
from ..domain.entity import Item, ItemStatus, ItemCategory
from ..domain.repository import ItemRepository
from .interfaces import ImageStorageService
from typing import Optional
class ItemService:
    def __init__(self, repo: ItemRepository, storage: ImageStorageService):
        self.repo = repo
        self.storage = storage

    def create_item(self, owner_id: str, title: str, description: str, category: ItemCategory, file_content: bytes, filename: str, content_type: str) -> Item:
        # 1. 上傳圖片
        image_url = self.storage.upload_image(file_content, filename, content_type)
        
        # 2. 建立 Item 物件
        new_item = Item(
            id=str(uuid.uuid4()),
            owner_id=owner_id,
            title=title,
            description=description,
            category=category,
            status=ItemStatus.AVAILABLE,
            image_url=image_url,
            created_at=datetime.now()
        )
        
        # 3. 存入 DB
        return self.repo.save(new_item)

    def search_items(self, keyword: Optional[str] = None, category: Optional[ItemCategory] = None):
        return self.repo.search(keyword, category)