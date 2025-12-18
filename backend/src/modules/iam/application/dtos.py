from pydantic import BaseModel, EmailStr
from typing import Optional

# --- Request (Input) ---
class GoogleLoginRequest(BaseModel):
    id_token: str  # 前端從 Google 拿到的 Token

# --- Response (Output) ---
class UserProfileResponse(BaseModel):
    id: str #資料庫中的user_id
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    is_admin: bool

    class Config:
        # 讓 Pydantic 可以直接讀取 Domain Entity (Python Object)
        from_attributes = True