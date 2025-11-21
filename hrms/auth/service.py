"""
權限管理系統
"""
from enum import Enum
from typing import Dict, List, Optional
from ..core.db.unit_of_work import UnitOfWork
from ..core.models import AuthorityCreate, AuthorityUpdate
from ..core.exceptions import AuthorizationError, RecordNotFoundError, DataValidationError
from pydantic import ValidationError


class Permission(Enum):
    """定義系統中的權限類型"""
    READ_EMPLOYEE = "read_employee"
    CREATE_EMPLOYEE = "create_employee"
    UPDATE_EMPLOYEE = "update_employee"
    DELETE_EMPLOYEE = "delete_employee"
    EXPORT_DATA = "export_data"
    VIEW_REPORTS = "view_reports"
    MANAGE_USERS = "manage_users"


class Role:
    """角色類別"""
    def __init__(self, role_id: str, name: str, permissions: List[Permission]):
        self.role_id = role_id
        self.name = name
        self.permissions = permissions

    def has_permission(self, permission: Permission) -> bool:
        """檢查角色是否具有特定權限"""
        return permission in self.permissions


# 預設角色
DEFAULT_ROLES = {
    "admin": Role("admin", "系統管理員", list(Permission)),
    "hr_manager": Role("hr_manager", "人事經理", [
        Permission.READ_EMPLOYEE,
        Permission.CREATE_EMPLOYEE,
        Permission.UPDATE_EMPLOYEE,
        Permission.DELETE_EMPLOYEE,
        Permission.EXPORT_DATA,
        Permission.VIEW_REPORTS
    ]),
    "hr_staff": Role("hr_staff", "人事專員", [
        Permission.READ_EMPLOYEE,
        Permission.CREATE_EMPLOYEE,
        Permission.UPDATE_EMPLOYEE,
        Permission.EXPORT_DATA
    ]),
    "employee": Role("employee", "一般員工", [
        Permission.READ_EMPLOYEE  # 只能查看自己的資料
    ])
}


class AuthService:
    """認證和授權服務"""
    
    @staticmethod
    def authenticate_user(account: str, password: str = None) -> Optional[Dict]:
        """
        認證用戶
        注意：在實際應用中，這裡應該與密碼驗證系統集成
        """
        # 簡化實現：假設所有帳戶都是有效的，但在實際應用中需要檢查密碼
        try:
            user = AuthService.get_user(account)
            if user and user.get("Active", False):
                return user
            return None
        except RecordNotFoundError:
            return None

    @staticmethod
    def authorize_user(account: str, permission: Permission) -> bool:
        """
        檢查用戶是否具有特定權限
        """
        user = AuthService.get_user(account)
        if not user:
            return False
        
        # 根據用戶的權限類型確定角色
        auth_type = user.get("Auth_Type", "")
        
        # 檢查是否為預設角色之一
        if auth_type in DEFAULT_ROLES:
            role = DEFAULT_ROLES[auth_type]
            return role.has_permission(permission)
        
        # 如果不是預設角色，則從 Authority 表獲取權限
        # 這需要更複雜的權限檢查邏輯，基於實際權限分配
        return False

    @staticmethod
    def get_user(account: str) -> Optional[Dict]:
        """獲取用戶資訊"""
        with UnitOfWork.from_settings() as uow:
            # 根據當前使用的後端類型決定如何獲取數據
            if hasattr(uow.adapter, 'get_by_pk'):
                return uow.adapter.get_by_pk("Authorities", "Account", account)
            else:
                # 使用通用方法
                records = uow.adapter.list("Authorities", filters={"Account": account})
                return records[0] if records else None

    @staticmethod
    def create_user(account: str, auth_type: str, active: bool = True) -> Dict:
        """創建新用戶"""
        user_data = {
            "Account": account,
            "Auth_Type": auth_type,
            "Active": active
        }
        
        # 驗證數據
        try:
            validated_data = AuthorityCreate(**user_data).model_dump()
        except ValidationError as e:
            raise DataValidationError(f"用戶數據驗證失敗: {e}")
        
        with UnitOfWork.from_settings() as uow:
            return uow.adapter.upsert("Authorities", "Account", validated_data)

    @staticmethod
    def update_user(account: str, **updates) -> Dict:
        """更新用戶資訊"""
        # 獲取當前用戶數據
        current_user = AuthService.get_user(account)
        if not current_user:
            raise RecordNotFoundError(f"用戶不存在: {account}")
        
        # 合併更新
        updated_data = {**current_user, **updates}
        
        # 驗證數據
        try:
            validated_data = AuthorityUpdate(**updated_data).model_dump()
        except ValidationError as e:
            raise DataValidationError(f"用戶數據驗證失敗: {e}")
        
        with UnitOfWork.from_settings() as uow:
            return uow.adapter.upsert("Authorities", "Account", validated_data)

    @staticmethod
    def delete_user(account: str) -> bool:
        """刪除用戶"""
        with UnitOfWork.from_settings() as uow:
            return uow.adapter.delete("Authorities", "Account", account)

    @staticmethod
    def list_users() -> List[Dict]:
        """列出所有用戶"""
        with UnitOfWork.from_settings() as uow:
            return uow.adapter.list("Authorities")


def require_permission(permission: Permission):
    """
    裝飾器：檢查當前用戶是否具有指定權限
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 在實際應用中，需要從某處獲取當前用戶信息
            # 這裡簡化為假設有一個全局當前用戶
            current_user = getattr(wrapper, 'current_user', 'admin')  # 默認為 admin 進行測試
            
            if not AuthService.authorize_user(current_user, permission):
                raise AuthorizationError(f"用戶 {current_user} 沒有 {permission.value} 權限")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 使用範例
if __name__ == "__main__":
    # 創建一個測試用戶
    try:
        test_user = AuthService.create_user("test_user", "hr_staff", True)
        print(f"創建用戶: {test_user}")
        
        # 檢查權限
        can_read = AuthService.authorize_user("test_user", Permission.READ_EMPLOYEE)
        print(f"用戶 test_user 是否有讀取員工權限: {can_read}")
        
        can_delete = AuthService.authorize_user("test_user", Permission.DELETE_EMPLOYEE)
        print(f"用戶 test_user 是否有刪除員工權限: {can_delete}")
        
        # 列出所有用戶
        all_users = AuthService.list_users()
        print(f"所有用戶: {all_users}")
        
    except Exception as e:
        print(f"測試權限系統時發生錯誤: {e}")