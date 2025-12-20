from dotenv import load_dotenv
load_dotenv()
import os
from .modules.iam.infrastructure.models import Base, UserModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .modules.inventory.infrastructure.models import ItemModel

# --- 設定 AWS RDS 連線 (同你原本的程式碼) ---
RDS_USER = os.getenv("DB_USER", "")
RDS_PASSWORD = os.getenv("DB_PASSWORD", "")
RDS_HOST = os.getenv("DB_HOST", "")
RDS_PORT = os.getenv("DB_PORT", "")
RDS_DB_NAME = os.getenv("DB_NAME", "")

DATABASE_URL = f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}"

engine = create_engine(DATABASE_URL, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# --- Dependency: 取得 DB Session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()