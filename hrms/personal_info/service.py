"""
個人訊息服務
"""
from typing import List, Dict, Optional
from ..core.db.unit_of_work import UnitOfWork
from ..core.models import PersonalInfoCreate, PersonalInfoUpdate
from ..core.exceptions import DataValidationError, RecordNotFoundError
from pydantic import ValidationError

def list_personal_info(only_active: bool = True, limit: int = None) -> List[Dict]:
    """
    獲取個人訊息列表
    """
    try:
        with UnitOfWork.from_settings() as uow:
            # 根據後端類型調用相應方法
            if hasattr(uow.adapter, 'list'):
                filters = {"Active": "true"} if only_active else None
                return uow.adapter.list("PersonalInfo", filters=filters, limit=limit)
            else:
                # 通用實現
                all_records = uow.adapter.list("PersonalInfo", limit=limit)
                if only_active:
                    return [rec for rec in all_records if rec.get("Active", "true") == "true"]
                return all_records
    except Exception as e:
        raise DataValidationError(f"獲取個人訊息列表時發生錯誤: {str(e)}")

def get_personal_info(emp_id: str) -> Optional[Dict]:
    """
    獲取特定員工的個人訊息
    """
    try:
        with UnitOfWork.from_settings() as uow:
            result = uow.adapter.get_by_pk("PersonalInfo", "EMP_ID", emp_id)
            if result is None:
                raise RecordNotFoundError(f"找不到員工編號 {emp_id} 的個人訊息")
            return result
    except RecordNotFoundError:
        raise
    except Exception as e:
        raise DataValidationError(f"獲取個人訊息時發生錯誤: {str(e)}")

def upsert_personal_info(data: Dict) -> Dict:
    """
    創建或更新個人訊息
    """
    # 使用 Pydantic 模型進行數據驗證
    try:
        if 'EMP_ID' in data and get_personal_info(data['EMP_ID']):
            # 更新現有記錄
            personal_info_data = PersonalInfoUpdate(**data)
        else:
            # 創建新記錄
            personal_info_data = PersonalInfoCreate(**data)
        
        validated_data = personal_info_data.model_dump()
    except ValidationError as e:
        raise DataValidationError(f"個人訊息驗證失敗: {e}")
    except RecordNotFoundError:
        # 如果記錄不存在，則創建新記錄
        try:
            personal_info_data = PersonalInfoCreate(**data)
            validated_data = personal_info_data.model_dump()
        except ValidationError as e:
            raise DataValidationError(f"個人訊息驗證失敗: {e}")
    
    try:
        with UnitOfWork.from_settings() as uow:
            return uow.adapter.upsert("PersonalInfo", "EMP_ID", validated_data)
    except Exception as e:
        raise DataValidationError(f"更新個人訊息時發生錯誤: {str(e)}")

def delete_personal_info(emp_id: str) -> bool:
    """
    刪除個人訊息
    """
    try:
        with UnitOfWork.from_settings() as uow:
            result = uow.adapter.delete("PersonalInfo", "EMP_ID", emp_id)
            if not result:
                raise RecordNotFoundError(f"找不到要刪除的員工編號 {emp_id} 的個人訊息")
            return result
    except RecordNotFoundError:
        raise
    except Exception as e:
        raise DataValidationError(f"刪除個人訊息時發生錯誤: {str(e)}")