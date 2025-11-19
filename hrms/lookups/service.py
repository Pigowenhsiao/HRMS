from __future__ import annotations
from typing import List
from ..core.db.unit_of_work import UnitOfWork

def list_dept_codes() -> List[str]:
    with UnitOfWork.from_settings() as uow:
        return uow.adapter.list_distinct("L_Section", "Dept_Code")

def list_areas() -> List[str]:
    with UnitOfWork.from_settings() as uow:
        return uow.adapter.list_distinct("Area", "Area")

def list_jobs() -> List[str]:
    with UnitOfWork.from_settings() as uow:
        return uow.adapter.list_distinct("L_Job", "L_Job")

def list_vac_types() -> List[str]:
    with UnitOfWork.from_settings() as uow:
        return uow.adapter.list_distinct("VAC_Type", "VAC_ID")
