# -*- coding: utf-8 -*-
"""
Access → CSV 匯出腳本

用途：
- 將 Access .mdb / .accdb 的資料表，批次匯出為 ./data/*.csv
- 依照 config/access_csv_mapping.yaml（若存在）進行表名/欄位 rename 與欄位順序調整
- 以 UTF-8-SIG 輸出，方便 Excel 開啟

需求：
- Windows 已安裝 Microsoft Access ODBC Driver
- pip install pyodbc pandas pyyaml

使用範例：
  python scripts/access_to_csv_export.py --mdb "C:\path\HRMS.mdb"
  python scripts/access_to_csv_export.py --dsn MyAccessDSN --out ./data
  python scripts/access_to_csv_export.py --mdb "C:\path\HRMS.accdb" --tables BASIC,Person_Info

備註：
- 未指定 --tables 時，會自動列出所有「一般資料表」（排除 MSys 前綴）。
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path
import pyodbc
import pandas as pd
import yaml

DEFAULT_MAPPING_FILE = "config/access_csv_mapping.yaml"

def load_mapping(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def connect_access(mdb: str | None, dsn: str | None) -> pyodbc.Connection:
    if not mdb and not dsn:
        raise SystemExit("請提供 --mdb 或 --dsn 其中之一")
    if dsn:
        conn_str = f"DSN={dsn};"
    else:
        # 以 Driver 直接連線（需安裝 Access ODBC Driver）
        mdb = os.path.abspath(mdb)
        driver = "{Microsoft Access Driver (*.mdb, *.accdb)}"
        conn_str = f"DRIVER={driver};DBQ={mdb};"
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print("連線失敗，請確認 ODBC Driver 與路徑/DSN 是否正確。")
        raise

def list_access_tables(conn: pyodbc.Connection) -> list[str]:
    # 只取一般 TABLE（排除系統表）
    cur = conn.cursor()
    rows = cur.tables(tableType="TABLE").fetchall()
    names = []
    for r in rows:
        tname = (r.table_name or "").strip()
        if not tname:
            continue
        if tname.lower().startswith("msys"):  # 排除系統表
            continue
        names.append(tname)
    return sorted(names)

def export_table_to_csv(conn: pyodbc.Connection, table: str, out_dir: Path,
                        mapping: dict) -> str:
    # 讀資料
    q = f"SELECT * FROM [{table}]"
    df = pd.read_sql(q, conn)
    df = df.astype("string").fillna("")

    # 應用 mapping（表名/欄位 rename 與欄位順序）
    tmap = (mapping.get("tables") or {}).get(table, {})
    csv_name = tmap.get("csv_name", table).upper()

    # 欄位 rename
    rename_map = tmap.get("rename", {}) or {}
    if rename_map:
        df = df.rename(columns=rename_map)

    # 欄位順序
    columns = tmap.get("columns", None)
    if columns:
        # 只保留列出的欄位，並依序排列（未列出者忽略）
        keep = [c for c in columns if c in df.columns]
        df = df[keep]

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{csv_name}.csv"
    # 使用 UTF-8 with BOM，Excel 開啟比較友善
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return str(out_path)

def main():
    ap = argparse.ArgumentParser(description="Access → CSV 批次匯出")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--mdb", help="Access 檔案路徑（.mdb/.accdb）")
    g.add_argument("--dsn", help="ODBC DSN 名稱")
    ap.add_argument("--tables", help="指定要匯出的表（逗號分隔）；未指定則匯出全部一般資料表")
    ap.add_argument("--out", default="./data", help="輸出資料夾（預設 ./data）")
    ap.add_argument("--mapping", default=DEFAULT_MAPPING_FILE, help="表/欄位對應 YAML（預設 config/access_csv_mapping.yaml）")
    args = ap.parse_args()

    out_dir = Path(args.out)
    mapping = load_mapping(args.mapping)

    with connect_access(args.mdb, args.dsn) as conn:
        if args.tables:
            tables = [t.strip() for t in args.tables.split(",") if t.strip()]
        else:
            tables = list_access_tables(conn)
        if not tables:
            print("未找到任何資料表。")
            return

        print(f"將匯出 {len(tables)} 張表 → {out_dir} ...")
        exported = []
        for t in tables:
            try:
                path = export_table_to_csv(conn, t, out_dir, mapping)
                exported.append((t, path))
                print(f"[OK] {t} -> {path}")
            except Exception as e:
                print(f"[ERR] 匯出 {t} 失敗：{e}")

        print("\n== 匯出完成 ==")
        for t, p in exported:
            print(f"{t} -> {p}")

if __name__ == "__main__":
    main()
