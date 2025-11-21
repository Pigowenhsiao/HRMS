from __future__ import annotations
from typing import List, Dict, Optional
from ..core.db.unit_of_work import UnitOfWork
from ..core.models import EmployeeCreate, EmployeeUpdate
from ..core.exceptions import DataValidationError, RecordNotFoundError
from pydantic import ValidationError

def list_employees(only_active: bool = True, limit: int | None = None) -> List[Dict]:
    from .repository import EmployeeRepositoryCSV
    try:
        with UnitOfWork.from_settings() as uow:
            repo = EmployeeRepositoryCSV(uow.adapter)
            return repo.list(only_active=only_active, limit=limit)
    except Exception as e:
        raise DataValidationError(f"獲取員工列表時發生錯誤: {str(e)}")

def get_employee(emp_id: str) -> Optional[Dict]:
    from .repository import EmployeeRepositoryCSV
    try:
        with UnitOfWork.from_settings() as uow:
            repo = EmployeeRepositoryCSV(uow.adapter)
            employee = repo.get(emp_id)
            if employee is None:
                raise RecordNotFoundError(f"找不到員工編號: {emp_id}")
            return employee
    except RecordNotFoundError:
        raise
    except Exception as e:
        raise DataValidationError(f"獲取員工資料時發生錯誤: {str(e)}")

def upsert_employee(row: Dict) -> Dict:
    from .repository import EmployeeRepositoryCSV

    # 使用 Pydantic 模型進行數據驗證
    try:
        if 'EMP_ID' in row and get_employee(row['EMP_ID']):
            # 更新現有員工
            employee_data = EmployeeUpdate(**row)
        else:
            # 創建新員工
            employee_data = EmployeeCreate(**row)

        validated_row = employee_data.model_dump()
    except ValidationError as e:
        raise DataValidationError(f"數據驗證失敗: {e}")

    try:
        with UnitOfWork.from_settings() as uow:
            repo = EmployeeRepositoryCSV(uow.adapter)
            return repo.upsert(validated_row)
    except Exception as e:
        raise DataValidationError(f"更新員工資料時發生錯誤: {str(e)}")

def delete_employee(emp_id: str) -> bool:
    from .repository import EmployeeRepositoryCSV
    try:
        with UnitOfWork.from_settings() as uow:
            repo = EmployeeRepositoryCSV(uow.adapter)
            result = repo.delete(emp_id)
            if not result:
                raise RecordNotFoundError(f"找不到要刪除的員工編號: {emp_id}")
            return result
    except RecordNotFoundError:
        raise
    except Exception as e:
        raise DataValidationError(f"刪除員工資料時發生錯誤: {str(e)}")
