from __future__ import annotations
from typing import List, Dict, Optional
from ..core.db.unit_of_work import UnitOfWork

def list_employees(only_active: bool = True, limit: int | None = None) -> List[Dict]:
    from .repository import EmployeeRepositoryCSV
    with UnitOfWork.from_settings() as uow:
        repo = EmployeeRepositoryCSV(uow.adapter)
        return repo.list(only_active=only_active, limit=limit)

def get_employee(emp_id: str) -> Optional[Dict]:
    from .repository import EmployeeRepositoryCSV
    with UnitOfWork.from_settings() as uow:
        repo = EmployeeRepositoryCSV(uow.adapter)
        return repo.get(emp_id)

def upsert_employee(row: Dict) -> Dict:
    from .repository import EmployeeRepositoryCSV
    with UnitOfWork.from_settings() as uow:
        repo = EmployeeRepositoryCSV(uow.adapter)
        return repo.upsert(row)

def delete_employee(emp_id: str) -> bool:
    from .repository import EmployeeRepositoryCSV
    with UnitOfWork.from_settings() as uow:
        repo = EmployeeRepositoryCSV(uow.adapter)
        return repo.delete(emp_id)
