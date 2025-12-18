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
        # 1. 新增這一步：先拿 Code 換 Token
        # 注意：這裡呼叫的是我們剛剛在 CognitoIdentityProvider 新寫的方法
        # 但因為我們在 interfaces.py 沒定義這個方法，Python 檢查可能會亮紅燈，但執行是沒問題的
        # (正規做法是要去 interfaces.py 補上定義，這裡先略過)
        id_token = self.identity_provider.exchange_code_for_token(request.code)

        # 2. 驗證 Token (原本的邏輯，傳入剛剛換到的 id_token)
        identity_data = self.identity_provider.verify_token(id_token)

        # 3. 檢查使用者是否存在 (以下邏輯完全不變)
        existing_user = self.user_repo.get_by_email(identity_data.email)

        if existing_user:
            user = existing_user
            user.name = identity_data.name
            user.avatar_url = identity_data.avatar_url
            self.user_repo.save(user)
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