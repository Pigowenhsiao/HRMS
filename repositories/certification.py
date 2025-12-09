"""
證照相關 Repository
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from domain.models import Certify, CertifyType, CertifyItem, TrainingRecord, CertifyRecord, CertifyToolMap
from .base import BaseRepositorySQLAlchemy

class CertifyRepository(BaseRepositorySQLAlchemy[Certify]):
    """證照狀態 Repository"""
    model_class = Certify
    
    def __init__(self, session: Session):
        super().__init__(session)

class CertifyTypeRepository(BaseRepositorySQLAlchemy[CertifyType]):
    """證照類型 Repository"""
    model_class = CertifyType
    
    def __init__(self, session: Session):
        super().__init__(session)

class CertifyItemRepository(BaseRepositorySQLAlchemy[CertifyItem]):
    """證照項目 Repository"""
    model_class = CertifyItem
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_by_dept(self, dept_code: str) -> List[CertifyItem]:
        """依部門查詢證照項目"""
        return self.list(filters={"Dept": dept_code})
    
    def get_by_type(self, certify_type: str) -> List[CertifyItem]:
        """依類型查詢證照項目"""
        return self.list(filters={"Certify_Type": certify_type})
    
    def delete(self, pk: tuple) -> bool:
        """
        刪除證照項目（支援複合主鍵）
        
        Args:
            pk: 複合主鍵元組 (Dept, Certify_ID)
        
        Returns:
            是否成功刪除
        """
        obj = self.get_by_pk(pk)
        if obj:
            self.session.delete(obj)
            return True
        return False

class TrainingRecordRepository(BaseRepositorySQLAlchemy[TrainingRecord]):
    """
    證照記錄 Repository（主要）
    處理員工證照記錄
    """
    model_class = TrainingRecord
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_by_employee(self, emp_id: str, only_active: bool = True) -> List[TrainingRecord]:
        """
        依員工查詢證照記錄
        
        Args:
            emp_id: 員工編號
            only_active: 是否只包含有效記錄
        
        Returns:
            證照記錄列表
        """
        filters = {"EMP_ID": emp_id}
        if only_active:
            filters["Active"] = True
        
        return self.list(filters=filters)
    
    def get_by_certify_item(self, certify_id: str) -> List[TrainingRecord]:
        """依證照項目查詢記錄"""
        return self.list(filters={"Certify_ID": certify_id})
    
    def get_expiring_records(self, days: int = 30) -> List[TrainingRecord]:
        """
        取得即將到期的證照記錄
        
        Args:
            days: 未來 N 天內到期
        
        Returns:
            即將到期的證照記錄列表
        """
        # Note: 這需要實作日期計算
        # 因為 Certify_date 是字串格式，需要特別處理
        # 這裡先回傳空列表，實作時需要根據日期格式處理
        return []
    
    def count_by_employee(self, emp_id: str) -> int:
        """計算員工的證照數量"""
        return self.count(filters={"EMP_ID": emp_id, "Active": True})

class CertifyRecordRepository(BaseRepositorySQLAlchemy[CertifyRecord]):
    """證照記錄 Repository（次要）"""
    model_class = CertifyRecord
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_by_employee(self, emp_id: str) -> List[CertifyRecord]:
        """依員工查詢證照記錄"""
        return self.list(filters={"EMP_ID": emp_id})

class CertifyToolMapRepository(BaseRepositorySQLAlchemy[CertifyToolMap]):
    """證照工具對應 Repository"""
    model_class = CertifyToolMap
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_by_certify(self, certify_id: str) -> List[CertifyToolMap]:
        """依證照查詢工具對應"""
        return self.list(filters={"Certify_ID": certify_id})
    
    def get_by_tool(self, tool_id: str) -> List[CertifyToolMap]:
        """依工具查詢證照對應"""
        return self.list(filters={"TOOL_ID": tool_id})


class CertificationService:
    """
    證照服務
    封裝證照相關的商業邏輯
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.certify_item_repo = CertifyItemRepository(session)
        self.training_record_repo = TrainingRecordRepository(session)
        self.certify_tool_map_repo = CertifyToolMapRepository(session)
    
    def get_employee_certifications(self, emp_id: str) -> Dict[str, Any]:
        """
        取得員工的完整證照資訊
        
        Args:
            emp_id: 員工編號
        
        Returns:
            包含證照記錄和統計的字典
        """
        records = self.training_record_repo.get_by_employee(emp_id)
        total_count = len(records)
        active_count = len([r for r in records if r.Active])
        
        return {
            "records": records,
            "statistics": {
                "total": total_count,
                "active": active_count,
                "inactive": total_count - active_count
            }
        }
    
    def get_certification_details(self, certify_id: str) -> Dict[str, Any]:
        """
        取得證照項目的詳細資訊
        
        Args:
            certify_id: 證照項目 ID
        
        Returns:
            包含證照項目、記錄、工具的字典
        """
        # 取得證照項目
        certify_item = self.certify_item_repo.get_by_pk(certify_id)
        
        # 取得相關記錄
        records = self.training_record_repo.get_by_certify_item(certify_id)
        
        # 取得相關工具
        tool_maps = self.certify_tool_map_repo.get_by_certify(certify_id)
        
        return {
            "certify_item": certify_item,
            "records": records,
            "tool_maps": tool_maps,
            "statistics": {
                "record_count": len(records),
                "tool_count": len(tool_maps)
            }
        }
