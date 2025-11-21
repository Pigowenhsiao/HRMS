"""
權限管理 API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..auth.service import AuthService, Permission
from ..core.models import AuthorityCreate, AuthorityUpdate

router = APIRouter(prefix="/auth", tags=["auth"])

def check_auth_permission():
    """檢查管理權限的依賴函數"""
    # 在實際應用中，這裡會檢查當前用戶的認證和授權狀態
    # 簡化實現中，我們假設管理員可以訪問所有管理功能
    pass

@router.get("/users", response_model=List[dict])
def list_users():
    """列出所有用戶"""
    try:
        return AuthService.list_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{account}", response_model=dict)
def get_user(account: str):
    """獲取特定用戶資訊"""
    try:
        user = AuthService.get_user(account)
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users", response_model=dict)
def create_user(user_data: AuthorityCreate, _: None = Depends(check_auth_permission)):
    """創建新用戶"""
    try:
        return AuthService.create_user(
            user_data.Account,
            user_data.Auth_Type,
            user_data.Active
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{account}", response_model=dict)
def update_user(account: str, user_data: AuthorityUpdate, _: None = Depends(check_auth_permission)):
    """更新用戶資訊"""
    try:
        updates = user_data.model_dump(exclude_unset=True)
        return AuthService.update_user(account, **updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{account}")
def delete_user(account: str, _: None = Depends(check_auth_permission)):
    """刪除用戶"""
    try:
        result = AuthService.delete_user(account)
        if not result:
            raise HTTPException(status_code=404, detail="用戶不存在")
        return {"message": "用戶已成功刪除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/permissions/{account}/{permission}")
def check_permission(account: str, permission: str):
    """檢查用戶是否具有特定權限"""
    try:
        # 將權限字串轉換為枚舉
        perm_enum = getattr(Permission, permission.upper(), None)
        if not perm_enum:
            raise HTTPException(status_code=400, detail="無效的權限類型")
        
        has_permission = AuthService.authorize_user(account, perm_enum)
        return {"account": account, "permission": permission, "has_permission": has_permission}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))