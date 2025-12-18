import uuid
from typing import Optional

# 引入 Domain 層的定義 (你的地基)
from ..domain.entity import User
from ..domain.repository import UserRepository

# 引入 Application 層的定義 (上面那兩個檔案)
from .dtos import GoogleLoginRequest, UserProfileResponse
from .interfaces import IdentityProvider

class AuthService:
    def __init__(self, user_repo: UserRepository, identity_provider: IdentityProvider):
        # 依賴注入：Service 不需要知道 DB 是 SQL 還是 Mongo，也不用知道是用 Cognito 還是 Firebase
        self.user_repo = user_repo
        self.identity_provider = identity_provider

    def login(self, request: GoogleLoginRequest) -> UserProfileResponse:
        # 1. 驗證 Token (委託給 infrastructure 實作去跑)
        # 如果 Token 無效，identity_provider 應該要拋出錯誤
        identity_data = self.identity_provider.verify_token(request.id_token)

        # 2. 檢查使用者是否存在 (Find)
        # 這裡假設用 Email 當唯一識別，你也可以改用 Cognito Sub ID
        existing_user = self.user_repo.get_by_email(identity_data.email)

        if existing_user:
            user = existing_user
            # (可選) 可以在這裡更新使用者的頭像或名字，保持資料同步
            # user.avatar_url = identity_data.avatar_url
            # self.user_repo.save(user)
        else:
            # 3. 如果不存在，自動註冊 (Create)
            new_user = User(
                id=str(uuid.uuid4()),  # 產生系統內部 ID
                email=identity_data.email,
                name=identity_data.name,
                password_hash="EXTERNAL_COGNITO",  # 標記為外部帳號
                avatar_url=identity_data.avatar_url,
                is_admin=False, # 預設權限
                is_active=True
            )
            # 存入資料庫
            user = self.user_repo.save(new_user)

        # 4. 將 Domain Entity 轉為 Response DTO
        return UserProfileResponse.model_validate(user)