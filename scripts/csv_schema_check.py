# -*- coding: utf-8 -*-
"""
CSV 欄位檢核腳本

用途：
- 將 data/*.csv 的欄位與 `config/csv_schema.yaml` 中的「期望欄位」比對
- 回報缺少/多出/順序不同等情形
- CI 中可作為品質檢查（成功=0；失敗=1）

使用：
  python scripts/csv_schema_check.py --data ./data --spec config/csv_schema.yaml
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path
import pandas as pd
import yaml

def load_spec(path: str) -> dict:
    if not os.path.exists(path):
        raise SystemExit(f"找不到 schema 規格檔：{path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def read_header(csv_path: Path) -> list[str]:
    import csv
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        header = next(r, [])
    return header

def main():
    ap = argparse.ArgumentParser(description="CSV 欄位檢核")
    ap.add_argument("--data", default="./data", help="CSV 目錄（預設 ./data）")
    ap.add_argument("--spec", default="config/csv_schema.yaml", help="欄位規格 YAML（預設 config/csv_schema.yaml）")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    tables = spec.get("tables", {})

    base = Path(args.data)
    if not base.exists():
        raise SystemExit(f"CSV 目錄不存在：{base}")

    ok = True
    for tbl, cfg in tables.items():
        csv_name = cfg.get("csv_name", tbl).upper()
        expected_cols = cfg.get("columns", [])
        pk = cfg.get("primary_key", None)

        csv_path = base / f"{csv_name}.csv"
        if not csv_path.exists():
            print(f"[MISS] 檔案不存在：{csv_path}")
            ok = False
            continue

        actual_cols = read_header(csv_path)
        missing = [c for c in expected_cols if c not in actual_cols]
        extra = [c for c in actual_cols if c not in expected_cols]

        if missing or extra:
            ok = False
            print(f"[ERR] {csv_name}.csv 欄位不符：")
            if missing:
                print(f"   - 缺少：{missing}")
            if extra:
                print(f"   - 多出：{extra}")
        else:
            if actual_cols != expected_cols:
                print(f"[WARN] {csv_name}.csv 欄位順序不同（不影響存取，但建議一致）")
            else:
                print(f"[OK] {csv_name}.csv 欄位一致")

        # 主鍵檢查（是否有空白）
        if pk and pk in actual_cols:
            import csv
            idx = actual_cols.index(pk)
            empty_pk = 0
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                r = csv.reader(f)
                next(r, None)
                for row in r:
                    if idx >= len(row) or (row[idx] or "").strip() == "":
                        empty_pk += 1
            if empty_pk > 0:
                ok = False
                print(f"[ERR] {csv_name}.csv 主鍵 {pk} 發現 {empty_pk} 筆空值")

    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
