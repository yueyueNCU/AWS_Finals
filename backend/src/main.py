from fastapi import FastAPI
from .modules.iam.presentation.router import router as iam_router # 引入 IAM 的 router

# 初始化 App
app = FastAPI(title="AWS Finals API")

# --- 註冊路由 (Include Routers) ---
# 這行指令會把 IAM 模組裡定義的所有 API (login, me) 都掛載進來
app.include_router(iam_router)

@app.get("/")
def read_root():
    return {"message": "Server is running!"}