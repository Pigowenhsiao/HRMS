"""
權限管理 Repository
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from domain.models import Authority, DelAuthority
from .base import BaseRepositorySQLAlchemy

class AuthorityRepository(BaseRepositorySQLAlchemy[Authority]):
    """使用者權限 Repository"""
    model_class = Authority
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_active_users(self) -> List[Authority]:
        """取得有效的使用者"""
        return self.list(filters={"Active": True})
    
    def get_by_account(self, account: str) -> Optional[Authority]:
        """依帳號查詢使用者"""
        return self.get_by_pk(account)
    
    def authenticate(self, account: str, auth_type: str) -> Optional[Authority]:
        """
        驗證使用者
        
        Args:
            account: 帳號
            auth_type: 權限類型
        
        Returns:
            Authority 或 None
        """
        filters = {
            "S_Account": account,
            "Active": True
        }
        if auth_type:
            filters["Auth_type"] = auth_type
        
        result = self.list(filters=filters, limit=1)
        return result[0] if result else None

class DelAuthorityRepository(BaseRepositorySQLAlchemy[DelAuthority]):
    """刪除權限 Repository"""
    model_class = DelAuthority
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_by_account(self, account_id: str) -> Optional[DelAuthority]:
        """依帳號查詢刪除權限"""
        return self.get(Account_ID=account_id)
    
    def has_delete_permission(self, account: str) -> bool:
        """
        檢查帳號是否有刪除權限
        
        Args:
            account: 帳號
        
        Returns:
            True/False
        """
        # 先檢查 DEL_AUTHORITY
        del_auth = self.get_by_pk(account)
        if del_auth and del_auth.Active:
            return del_auth.Del_Auth
        
        # 若無設定，檢查 Authority.Auth_type
        from .authority import AuthorityRepository
        auth_repo = AuthorityRepository(self.session)
        user = auth_repo.get_by_account(account)
        
        # Auth_type = 01 (Admin) 有刪除權限
        if user and user.Auth_type == "01":
            return True
        
        return False
    
    def list_users_with_delete_permission(self) -> List[Dict[str, Any]]:
        """
        列出有刪除權限的使用者
        
        Returns:
            使用者列表
        """
        # 查詢 Authority
        auth_repo = AuthorityRepository(self.session)
        users = auth_repo.get_active_users()
        
        result = []
        for user in users:
            has_permission = self.has_delete_permission(user.S_Account)
            result.append({
                "account": user.S_Account,
                "auth_type": user.Auth_type,
                "can_delete": has_permission,
                "active": user.Active
            })
        
        return result


class AuthorizationService:
    """
    權限服務
    處理使用者驗證與權限檢查
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.auth_repo = AuthorityRepository(session)
        self.del_auth_repo = DelAuthorityRepository(session)
    
    def login(self, account: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        使用者登入
        
        Args:
            account: 帳號
            password: 密碼（目前未使用）
        
        Returns:
            登入結果字典
        """
        user = self.auth_repo.get_by_account(account)
        
        if not user:
            return {"success": False, "message": "帳號不存在"}
        
        if not user.Active:
            return {"success": False, "message": "帳號已停用"}
        
        # 檢查刪除權限
        can_delete = self.del_auth_repo.has_delete_permission(account)
        
        return {
            "success": True,
            "user": {
                "account": user.S_Account,
                "auth_type": user.Auth_type,
                "can_delete": can_delete
            }
        }
    
    def check_permission(self, account: str, permission: str) -> bool:
        """
        檢查使用者權限
        
        Args:
            account: 帳號
            permission: 權限類型（'delete', 'admin'）
        
        Returns:
            True/False
        """
        if permission == "delete":
            return self.del_auth_repo.has_delete_permission(account)
        elif permission == "admin":
            user = self.auth_repo.get_by_account(account)
            return user and user.Auth_type == "01" and user.Active
        
        return False
