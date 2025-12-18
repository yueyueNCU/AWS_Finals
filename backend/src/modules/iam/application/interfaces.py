from typing import Protocol, Optional
from dataclasses import dataclass

# --- 定義從 Cognito/Google 解開後的標準資料格式 ---
@dataclass
class IdentityData:
    email: str
    name: str
    avatar_url: Optional[str]
    # sub: str  # 如果想用 Cognito ID 當主鍵，可以加這個欄位

# --- 定義身分驗證器的合約 (Protocol) ---
# 任何想當驗證器的程式 (例如 CognitoIdentityProvider)，都必須實作這個方法
class IdentityProvider(Protocol):
    def verify_token(self, token: str) -> IdentityData:
        ...
    def exchange_code_for_token(self, code: str) -> str:
        ...