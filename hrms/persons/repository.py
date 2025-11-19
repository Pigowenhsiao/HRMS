from __future__ import annotations
from typing import List, Dict, Optional
from ..core.db.repository import BaseRepository

TABLE = "BASIC"
PK = "EMP_ID"

class EmployeeRepositoryCSV(BaseRepository):
    def list(self, only_active: bool = True, limit: int | None = None) -> List[Dict]:
        filt = None
        if only_active:
            filt = {"Active": "true"}
        return self.adapter.list(TABLE, filters=filt, limit=limit)

    def get(self, emp_id: str) -> Optional[Dict]:
        return self.adapter.get_by_pk(TABLE, PK, emp_id)

    def upsert(self, row: Dict) -> Dict:
        # 正規化布林字串
        if "Active" in row:
            v = str(row["Active"]).strip().lower()
            row["Active"] = "true" if v in ("1","true","y","yes") else "false"
        return self.adapter.upsert(TABLE, PK, row)

    def delete(self, emp_id: str) -> bool:
        return self.adapter.delete(TABLE, PK, emp_id)
