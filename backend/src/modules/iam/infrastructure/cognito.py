import requests
import time
from jose import jwk, jwt
from jose.utils import base64url_decode
from ..application.interfaces import IdentityProvider, IdentityData

class CognitoIdentityProvider(IdentityProvider):
    def __init__(self, region: str, user_pool_id: str, app_client_id: str):
        self.region = region
        self.user_pool_id = user_pool_id
        self.app_client_id = app_client_id
        
        # 這是 AWS Cognito 存放公鑰的標準網址
        self.jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        self._keys = None # 用來快取公鑰，不用每次都去下載

    def _get_keys(self):
        """下載並快取 AWS 的公鑰"""
        if not self._keys:
            response = requests.get(self.jwks_url)
            self._keys = response.json()['keys']
        return self._keys

    def verify_token(self, token: str) -> IdentityData:
        # 1. 取得 Token Header (未驗證前先看 Header)
        try:
            headers = jwt.get_unverified_header(token)
        except Exception:
            raise ValueError("Invalid token header")

        # 2. 找對應的公鑰 (Key ID matching)
        kid = headers.get('kid')
        keys = self._get_keys()
        key_index = -1
        
        for i in range(len(keys)):
            if kid == keys[i]['kid']:
                key_index = i
                break
        
        if key_index == -1:
            raise ValueError('Public key not found in JWKS')

        # 3. 建構公鑰物件
        public_key = jwk.construct(keys[key_index])

        # 4. 驗證簽章、過期時間、Audience
        # 這一步如果失敗，python-jose 會直接噴 error
        message, encoded_signature = str(token).rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

        if not public_key.verify(message.encode("utf8"), decoded_signature):
            raise ValueError('Signature verification failed')

        claims = jwt.get_unverified_claims(token)

        # 驗證 Token 是否過期
        if time.time() > claims['exp']:
            raise ValueError('Token is expired')
            
        # 驗證這張 Token 是否發給我們的 App Client (避免拿別的 App 的 Token 來騙)
        if claims['aud'] != self.app_client_id:
            raise ValueError('Token was not issued for this audience')

        email = claims.get('email')
        if not email:
            raise ValueError("Token is missing 'email' claim")
        
        # 5. 轉換成統一的 IdentityData 格式
        return IdentityData(
            email=email,
            name=claims.get('name', 'Unknown User'), # Cognito 不一定有 name
            avatar_url=claims.get('picture'),        # Cognito 的圖片欄位通常叫 picture
            # sub=claims.get('sub')                  # 如果你需要 Cognito ID
        )