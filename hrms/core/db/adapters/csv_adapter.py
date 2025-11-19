from __future__ import annotations
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
from filelock import FileLock
import os

class CSVAdapter:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)

    # ---------- helpers ----------
    def _csv_path(self, table: str) -> Path:
        return self.data_dir / f"{table.upper()}.csv"

    def _ensure_exists(self, table: str):
        p = self._csv_path(table)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            # 建立空檔含表頭（暫時無欄位，等第一次 upsert 時再補）
            p.write_text("", encoding="utf-8")

    def _read_df(self, table: str) -> pd.DataFrame:
        p = self._csv_path(table)
        if not p.exists() or p.stat().st_size == 0:
            return pd.DataFrame()
        return pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8")

    def _write_df(self, table: str, df: pd.DataFrame):
        p = self._csv_path(table)
        lock = FileLock(str(p) + ".lock")
        with lock:
            df.to_csv(p, index=False, encoding="utf-8")

    # ---------- CRUD ----------
    def list(self, table: str, filters: Optional[Dict[str, str]] = None, limit: Optional[int] = None) -> List[Dict]:
        df = self._read_df(table)
        if filters:
            for k, v in filters.items():
                if k in df.columns:
                    df = df[df[k].astype(str) == str(v)]
        if limit is not None:
            df = df.head(limit)
        return df.to_dict(orient="records")

    def get_by_pk(self, table: str, pk: str, value: str) -> Optional[Dict]:
        df = self._read_df(table)
        if pk not in df.columns:
            return None
        rows = df[df[pk].astype(str) == str(value)]
        if rows.empty:
            return None
        rec = rows.iloc[0].to_dict()
        return rec

    def upsert(self, table: str, pk: str, row: Dict) -> Dict:
        # 讀檔 → 更新或追加 → 寫回
        df = self._read_df(table)
        # 若空表，建立欄位
        if df.empty:
            df = pd.DataFrame(columns=list(row.keys()))
        # 確保所有欄位存在
        for col in row.keys():
            if col not in df.columns:
                df[col] = ""
        row = {k: ("" if v is None else str(v)) for k, v in row.items()}
        if pk not in df.columns:
            df[pk] = ""
        mask = df[pk].astype(str) == str(row.get(pk, ""))
        if mask.any():
            df.loc[mask, list(row.keys())] = list(row.values())
        else:
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        self._write_df(table, df)
        return row

    def delete(self, table: str, pk: str, value: str) -> bool:
        df = self._read_df(table)
        if df.empty or pk not in df.columns:
            return False
        before = len(df)
        df = df[df[pk].astype(str) != str(value)]
        if len(df) == before:
            return False
        self._write_df(table, df)
        return True

    def list_distinct(self, table: str, column: str) -> List[str]:
        df = self._read_df(table)
        if df.empty or column not in df.columns:
            return []
        return [str(x) for x in df[column].dropna().astype(str).drop_duplicates().sort_values().tolist()]
