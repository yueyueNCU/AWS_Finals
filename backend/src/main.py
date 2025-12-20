from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <--- 1. 必須引入這個# <--- 2. 建議引入這個，確保讀得到 .env
from dotenv import load_dotenv
load_dotenv()

from .modules.iam.presentation.router import router as iam_router # 引入 IAM 的 router
from .modules.inventory.presentation.router import router as inventory_router
# 初始化 App
app = FastAPI(title="AWS Finals API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.yueyue.site"], # 指定前端網址，或用 ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 註冊路由 (Include Routers) ---
# 這行指令會把 IAM 模組裡定義的所有 API (login, me) 都掛載進來
app.include_router(iam_router)
app.include_router(inventory_router)

@app.get("/")
def read_root():
    return {"message": "Server is running!"}