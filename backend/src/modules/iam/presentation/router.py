from fastapi import APIRouter, Depends, HTTPException
from ..application.dtos import GoogleLoginRequest, UserProfileResponse
from ..application.service import AuthService
from ..domain.entity import User
from ..dependencies import get_auth_service, get_current_user # 引入剛剛寫好的 dependencies

# 建立 Router
router = APIRouter(
    prefix="/auth",   # 路由前綴，例如 /auth/login
    tags=["Auth"]     # 在 Swagger UI 上的分類標籤
)

@router.post("/login", response_model=UserProfileResponse)
def login(
    request: GoogleLoginRequest, 
    service: AuthService = Depends(get_auth_service)
):
    try:
        user_profile = service.login(request)
        return user_profile
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hello, {current_user.name}",
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "id": current_user.id
    }