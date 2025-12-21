from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import ValidationError

# 引入 IAM 模組的驗證功能 (確保只有登入的使用者能刊登)
from ...iam.dependencies import get_current_user
from ...iam.domain.entity import User

# 引入 Items 模組的 Service 與 DTO
from ..application.service import ItemService
from ..application.dtos import ItemResponse
from ..domain.entity import ItemCategory
from ..dependencies import get_item_service

# 定義 Router
router = APIRouter(
    prefix="/items",   # 所有這個檔案的 API 都會以 /items 開頭
    tags=["Items"]     # Swagger UI 上的分類標籤
)

# ---------------------------------------------
# 1. 刊登物品 (Create Item) - 支援圖片上傳
# ---------------------------------------------
@router.post(
    "/", 
    response_model=ItemResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="刊登新物品 (需上傳圖片)"
)
async def create_item(
    # 使用 Form(...) 來接收表單欄位，因為要配合檔案上傳 (Multipart)
    title: str = Form(..., description="物品標題"),
    description: str = Form(..., description="物品詳細說明"),
    category: ItemCategory = Form(..., description="物品分類 (TEXTBOOK, 3C, DAILY, OTHER)"),
    
    # 使用 File(...) 來接收圖片檔案
    image: UploadFile = File(..., description="物品照片"),
    
    # 依賴注入：取得當前登入的使用者 (如果沒登入會報錯 401)
    current_user: User = Depends(get_current_user),
    
    # 依賴注入：取得 ItemService
    service: ItemService = Depends(get_item_service)
):
    """
    刊登物品的 API。
    前端需使用 'multipart/form-data' 格式發送 Request。
    """
    # 簡單驗證檔案類型 (可選)
    if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only JPEG or PNG images are allowed.")

    # 讀取檔案內容 (bytes)
    file_content = await image.read()

    try:
        # 呼叫 Service 處理業務邏輯 (上傳 S3 + 寫入 DB)
        new_item = service.create_item(
            owner_id=current_user.id,
            title=title,
            description=description,
            category=category,
            file_content=file_content,
            filename=image.filename or "unknown_file",
            content_type=image.content_type
        )
        new_item.owner_name = current_user.name
        
        return new_item
        
    except Exception as e:
        # 捕捉未預期的錯誤
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------
# 2. 搜尋/列表物品 (Search Items)
# ---------------------------------------------
@router.get(
    "/", 
    response_model=List[ItemResponse],
    summary="搜尋物品列表"
)
def search_items(
    keyword: Optional[str] = None,
    category: Optional[ItemCategory] = None,
    service: ItemService = Depends(get_item_service)
):
    """
    取得所有上架中 (AVAILABLE) 的物品。
    可以透過 Query Parameters 進行篩選：
    - ?keyword=計算機 (搜尋標題)
    - ?category=3C (篩選分類)
    """
    return service.search_items(keyword, category)

# ---------------------------------------------
# 3. 取得目前登入使用者的所有物品 (包含歷史狀態)
# ---------------------------------------------
@router.get(
    "/me", 
    response_model=List[ItemResponse],
    summary="取得我的物品清單 (含歷史紀錄)"
)
def get_my_items(
    current_user: User = Depends(get_current_user),
    service: ItemService = Depends(get_item_service)
):
    """
    取得當前登入使用者刊登過的所有物品，包含：
    - AVAILABLE (上架中)
    - TRADING (交易洽談中)
    - TRADED (已交換)
    - HIDDEN (下架)
    """
    return service.get_user_items(current_user.id)

# ---------------------------------------------
# 4. 取得單一物品詳情 (Get Item Detail)
# ---------------------------------------------
@router.get(
    "/{item_id}", 
    response_model=ItemResponse,
    summary="取得特定物品詳情"
)
def get_item(
    item_id: str,
    service: ItemService = Depends(get_item_service)
):
    # 這裡假設你的 Service 有實作 get_item_by_id (建議補上)
    # 如果沒有，可以直接用 repo: item = service.repo.get_by_id(item_id)
    item = service.repo.get_by_id(item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    return item