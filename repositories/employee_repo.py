from sqlalchemy.orm import Session
from ..domain.models.employee import Basic

class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    # 查詢：全部或僅 Active
    def list(self, only_active: bool = True, limit: int | None = None):
        q = self.db.query(Basic)
        if only_active:
            q = q.filter(Basic.Active == True)
        if limit:
            q = q.limit(limit)
        return q.all()

    def get(self, emp_id: str):
        return self.db.get(Basic, emp_id)

    def upsert(self, emp_id: str, dept_code: str | None, c_name: str | None,
               on_board_date: str | None, area: str | None, active: bool = True):
        obj = self.get(emp_id)
        if obj is None:
            obj = Basic(EMP_ID=emp_id, Dept_Code=dept_code, C_Name=c_name,
                        On_Board_Date=on_board_date, Area=area, Active=active)
            self.db.add(obj)
        else:
            obj.Dept_Code = dept_code
            obj.C_Name = c_name
            obj.On_Board_Date = on_board_date
            obj.Area = area
            obj.Active = active
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, emp_id: str):
        obj = self.get(emp_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
