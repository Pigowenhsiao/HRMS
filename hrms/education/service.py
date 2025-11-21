"""
教育經歷服務
"""
from typing import List, Dict, Optional
from ..core.db.unit_of_work import UnitOfWork
from ..education.models import EducationCreate, EducationUpdate
from ..core.exceptions import DataValidationError, RecordNotFoundError
from pydantic import ValidationError

def list_education_records(emp_id: str = None, limit: int = None) -> List[Dict]:
    """
    獲取教育經歷記錄列表
    """
    try:
        with UnitOfWork.from_settings() as uow:
            filters = {"EMP_ID": emp_id} if emp_id else None
            return uow.adapter.list("Education", filters=filters, limit=limit)
    except Exception as e:
        raise DataValidationError(f"獲取教育經歷記錄時發生錯誤: {str(e)}")

def get_education_record(edu_id: int) -> Optional[Dict]:
    """
    獲取特定教育經歷記錄
    """
    try:
        with UnitOfWork.from_settings() as uow:
            # 由於教育經歷表使用自動編號作為主鍵，我們需要根據具體的後端類型來實現
            all_records = uow.adapter.list("Education")
            for record in all_records:
                if int(record.get("Education_ID", 0)) == edu_id:
                    return record
            raise RecordNotFoundError(f"找不到教育經歷ID {edu_id}")
    except RecordNotFoundError:
        raise
    except Exception as e:
        raise DataValidationError(f"獲取教育經歷記錄時發生錯誤: {str(e)}")

def create_education_record(data: Dict) -> Dict:
    """
    創建教育經歷記錄
    """
    # 使用 Pydantic 模型進行數據驗證
    try:
        education_data = EducationCreate(**data)
        validated_data = education_data.model_dump()
    except ValidationError as e:
        raise DataValidationError(f"教育經歷數據驗證失敗: {e}")
    
    try:
        with UnitOfWork.from_settings() as uow:
            # 假設 Educaiton_ID 是自動編號，所以不包含在 upsert 中
            data_for_insert = {k: v for k, v in validated_data.items() if k != 'Education_ID'}
            return uow.adapter.upsert("Education", "EMP_ID", data_for_insert)
    except Exception as e:
        raise DataValidationError(f"創建教育經歷記錄時發生錯誤: {str(e)}")

def update_education_record(edu_id: int, data: Dict) -> Dict:
    """
    更新教育經歷記錄
    """
    try:
        # 獲取當前記錄
        current_record = get_education_record(edu_id)
        
        # 驗證更新數據
        try:
            education_data = EducationUpdate(**{**current_record, **data})
            validated_data = education_data.model_dump(exclude_unset=True)
        except ValidationError as e:
            raise DataValidationError(f"教育經歷數據驗證失敗: {e}")
        
        with UnitOfWork.from_settings() as uow:
            # 這是一個簡化的實現，因為 Education_ID 是自動編號
            # 在實際情況下，可能需要更具體的主鍵字段
            # 這裡我們假設通過其他唯一字段進行更新
            if 'Education_ID' in validated_data:
                del validated_data['Education_ID']
            
            # 將更新應用到匹配的記錄
            all_records = uow.adapter.list("Education")
            updated = False
            for record in all_records:
                if int(record.get("Education_ID", 0)) == edu_id:
                    # 找到匹配的記錄，構建更新後的數據
                    updated_record = {**record, **validated_data}
                    # 使用 EMP_ID 作為主鍵進行更新
                    return uow.adapter.upsert("Education", "EMP_ID", updated_record)
            
            if not updated:
                raise RecordNotFoundError(f"無法更新教育經歷ID {edu_id}，記錄不存在")
                
    except RecordNotFoundError:
        raise
    except Exception as e:
        raise DataValidationError(f"更新教育經歷記錄時發生錯誤: {str(e)}")

def delete_education_record(edu_id: int) -> bool:
    """
    刪除教育經歷記錄
    注意：此功能在當前架構下可能無法正常工作，因為我們使用的是基於 EMP_ID 的 upsert 操作
    而不是基於 Education_ID 的刪除操作
    """
    try:
        # 這是一個簡化的實現
        # 在實際情況下，您可能需要實現一個基於 Education_ID 的刪除功能
        # 或者添加一個邏輯刪除字段
        current_record = get_education_record(edu_id)
        emp_id = current_record['EMP_ID']
        
        # 在當前實現中，我們無法直接按 Education_ID 刪除
        # 所以這裡只是返回 False 來表示此操作目前不可用
        raise NotImplementedError("按ID刪除教育經歷記錄的功能尚未實現")
        
    except RecordNotFoundError:
        raise
    except NotImplementedError as e:
        raise e
    except Exception as e:
        raise DataValidationError(f"刪除教育經歷記錄時發生錯誤: {str(e)}")