# backend/src/main.py

import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 引入你的模組
from .modules.iam.infrastructure.models import Base
from .modules.iam.infrastructure.repository import SqlAlchemyUserRepository
from .modules.iam.infrastructure.cognito import CognitoIdentityProvider
from .modules.iam.application.service import AuthService
from .modules.iam.application.dtos import GoogleLoginRequest, UserProfileResponse

from dotenv import load_dotenv
load_dotenv()

# --- 設定 AWS RDS 連線 (同你原本的程式碼) ---
RDS_USER = os.getenv("DB_USER", "postgres")
RDS_PASSWORD = os.getenv("DB_PASSWORD", "password")
print(RDS_PASSWORD)
RDS_HOST = os.getenv("DB_HOST", "localhost")
RDS_PORT = os.getenv("DB_PORT", "5432")
RDS_DB_NAME = os.getenv("DB_NAME", "my_user_db")

DATABASE_URL = f"postgresql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# --- FastAPI App 初始化 ---
app = FastAPI(title="AWS Finals API")

# --- Dependency Injection (相依性注入) ---
# 1. 取得 DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. 取得 AuthService
# 這樣做的好處是 FastAPI 會自動幫你把 DB session 注入進去
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    # 設定 AWS Cognito 參數 (記得設環境變數)
    region = os.getenv("AWS_REGION", "us-east-1")
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID", "us-east-1_xxxxxx")
    app_client_id = os.getenv("COGNITO_APP_CLIENT_ID", "xxxxxx")
    
    user_repo = SqlAlchemyUserRepository(db)
    identity_provider = CognitoIdentityProvider(region, user_pool_id, app_client_id)
    
    return AuthService(user_repo, identity_provider)

# --- API Routes (路由) ---
@app.get("/")
def read_root():
    return {"message": "Server is running!"}

@app.post("/auth/login", response_model=UserProfileResponse)
def login(
    request: GoogleLoginRequest, 
    service: AuthService = Depends(get_auth_service)
):
    try:
        # 這裡會呼叫你寫好的 Service 邏輯
        user_profile = service.login(request)
        return user_profile
    except ValueError as e:
        # 處理驗證失敗 (例如 Token 過期)
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        # 處理其他錯誤
        raise HTTPException(status_code=500, detail=str(e))