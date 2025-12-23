import os
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# 引入剛剛分出去的 get_db
from ...database import get_db 

# 引入 IAM 內部的類別
from .infrastructure.repository import SqlAlchemyUserRepository
from .infrastructure.cognito import CognitoIdentityProvider
from .application.service import AuthService
from .domain.entity import User

# 定義 HTTPBearer
security = HTTPBearer()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    region = os.getenv("AWS_COGNITO_REGION", "")
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID", "")
    app_client_id = os.getenv("COGNITO_APP_CLIENT_ID", "")
    cognito_domain = os.getenv("COGNITO_DOMAIN", "")
    redirect_uri = os.getenv("COGNITO_REDIRECT_URI", "")
    client_secret = os.getenv("COGNITO_CLIENT_SECRET", "") 

    user_repo = SqlAlchemyUserRepository(db)
    
    identity_provider = CognitoIdentityProvider(
        region, 
        user_pool_id, 
        app_client_id, 
        cognito_domain, 
        redirect_uri,
        client_secret
    )
    
    return AuthService(user_repo, identity_provider)

def get_current_user(
    token: HTTPAuthorizationCredentials = Security(security),
    service: AuthService = Depends(get_auth_service)
) -> User:
    try:
        id_token = token.credentials
        identity_data = service.identity_provider.verify_token(id_token)
        user = service.user_repo.get_by_email(identity_data.email)
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        return user
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))