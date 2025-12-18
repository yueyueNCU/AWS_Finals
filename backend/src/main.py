import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .modules.iam.infrastructure.models import Base

# --- 設定 AWS RDS 連線資訊 ---
# 建議：不要把密碼直接寫在程式碼裡！請使用環境變數 (os.getenv)
# 你可以在電腦上執行 `export DB_PASSWORD=你的密碼`，或是使用 .env 檔案
RDS_USER = os.getenv("DB_USER", "postgres")        # AWS RDS 的 Master Username
RDS_PASSWORD = os.getenv("DB_PASSWORD", "mypassword") # AWS RDS 的 Master Password
RDS_HOST = os.getenv("DB_HOST", "my-rds-instance.xxxx.us-east-1.rds.amazonaws.com") # Endpoint
RDS_PORT = os.getenv("DB_PORT", "5432")            # PostgreSQL 預設 5432, MySQL 預設 3306
RDS_DB_NAME = os.getenv("DB_NAME", "my_project_db") # 你在 RDS 裡建立的資料庫名稱

# 組合連線字串 (Connection String)
# 格式: postgresql://帳號:密碼@網址:Port/資料庫名
DATABASE_URL = f"postgresql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}"

# 如果是用 MySQL，格式如下：
# DATABASE_URL = f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}"

# --- 建立 Engine ---
# 注意：RDS 不需要 connect_args={"check_same_thread": False}，那是 SQLite 專用的
engine = create_engine(DATABASE_URL)

# --- 建立 Session工廠 ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 初始化資料表 ---
# 這行會自動連上 RDS，檢查有沒有 users 表格，沒有的話就自動建立 (Create Table)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()