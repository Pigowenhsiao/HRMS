"""
員工相關 Repository
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from domain.models import Basic, PersonInfo
from .base import BaseRepositorySQLAlchemy

class BasicRepository(BaseRepositorySQLAlchemy[Basic]):
    """
    員工基本資料 Repository
    """
    model_class = Basic
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def search_by_name(self, name: str, only_active: bool = True, limit: int = 100) -> List[Basic]:
        """
        依姓名模糊搜尋
        
        Args:
            name: 姓名關鍵字
            only_active: 是否只搜尋在職員工
            limit: 回傳筆數限制
        
        Returns:
            員工列表
        """
        query = self.session.query(Basic)
        
        if only_active:
            query = query.filter(Basic.Active == True)
        
        if name:
            query = query.filter(Basic.C_Name.like(f"%{name}%"))
        
        return query.limit(limit).all()
    
    def get_by_dept(self, dept_code: str, only_active: bool = True) -> List[Basic]:
        """
        依部門查詢員工
        
        Args:
            dept_code: 部門代碼
            only_active: 是否只搜尋在職員工
        
        Returns:
            員工列表
        """
        filters = {"Dept_Code": dept_code}
        if only_active:
            filters["Active"] = True
        
        return self.list(filters=filters)
    
    def get_active_employees(self, limit: Optional[int] = None) -> List[Basic]:
        """
        取得所有在職員工
        
        Args:
            limit: 回傳筆數限制
        
        Returns:
            員工列表
        """
        return self.list(
            filters={"Active": True},
            limit=limit
        )
    
    def has_department_employees(self, dept_code: str) -> bool:
        """
        檢查部門是否有員工
        
        Args:
            dept_code: 部門代碼
        
        Returns:
            True/False
        """
        count = self.count(filters={"Dept_Code": dept_code})
        return count > 0


class PersonInfoRepository(BaseRepositorySQLAlchemy[PersonInfo]):
    """
    員工個人資訊 Repository
    """
    model_class = PersonInfo
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_by_employee_id(self, emp_id: str) -> Optional[PersonInfo]:
        """
        依員工編號查詢個人資訊
        
        Args:
            emp_id: 員工編號
        
        Returns:
            PersonInfo 或 None
        """
        return self.get(EMP_ID=emp_id)
    
    def upsert_by_employee_id(self, emp_id: str, data: Dict[str, Any]) -> PersonInfo:
        """
        依員工編號新增或更新個人資訊
        
        Args:
            emp_id: 員工編號
            data: 個人資訊資料
        
        Returns:
            PersonInfo
        """
        # 確保 EMP_ID 在資料中
        data["EMP_ID"] = emp_id
        return self.upsert(emp_id, data)
