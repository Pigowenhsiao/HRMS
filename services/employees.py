from ..db import get_session
from ..repositories.employee_repo import EmployeeRepository

def list_employees(only_active: bool = True, limit: int | None = None):
    with get_session() as s:
        return EmployeeRepository(s).list(only_active=only_active, limit=limit)

def get_employee(emp_id: str):
    with get_session() as s:
        return EmployeeRepository(s).get(emp_id)

def upsert_employee(emp_id: str, dept_code: str | None, c_name: str | None,
                    on_board_date: str | None, area: str | None, active: bool = True):
    with get_session() as s:
        return EmployeeRepository(s).upsert(emp_id, dept_code, c_name, on_board_date, area, active)

def delete_employee(emp_id: str) -> bool:
    with get_session() as s:
        return EmployeeRepository(s).delete(emp_id)
