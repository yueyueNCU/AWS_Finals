from fastapi import Depends
from sqlalchemy.orm import Session
from ...database import get_db
from .infrastructure.repository import SqlAlchemyItemRepository
from .infrastructure.s3_uploader import S3ImageStorage
from .application.service import ItemService

def get_item_service(db: Session = Depends(get_db)) -> ItemService:
    repo = SqlAlchemyItemRepository(db)
    storage = S3ImageStorage()
    return ItemService(repo, storage)