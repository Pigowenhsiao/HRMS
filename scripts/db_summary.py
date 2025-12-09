#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫摘要報告工具
快速查看 SQLite 資料庫中所有資料表的統計資訊
"""
from sqlalchemy import create_engine, inspect, text
from pathlib import Path
import sys

# 專案路徑
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQLITE_PATH = PROJECT_ROOT / "hrms.db"

def main():
    """主函式"""
    if not SQLITE_PATH.exists():
        print(f"✗ 資料庫檔案不存在: {SQLITE_PATH}")
        return 1
    
    db_url = f"sqlite:///{SQLITE_PATH}"
    engine = create_engine(db_url, echo=False)
    
    print("=" * 70)
    print("HRMS SQLite 資料庫摘要報告")
    print("=" * 70)
    print(f"資料庫位置: {SQLITE_PATH}")
    print(f"資料庫大小: {SQLITE_PATH.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    inspector = inspect(engine)
    table_names = sorted(inspector.get_table_names())
    
    print(f"資料表總數: {len(table_names)}")
    print()
    
    # 統計所有資料表的筆數
    total_rows = 0
    table_stats = []
    
    with engine.begin() as conn:
        for table_name in table_names:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                total_rows += count
                
                # 取得欄位數
                columns = inspector.get_columns(table_name)
                column_count = len(columns)
                
                table_stats.append({
                    "table_name": table_name,
                    "row_count": count,
                    "column_count": column_count
                })
            except Exception as e:
                print(f"✗ 查詢 {table_name} 失敗: {e}")
    
    # 依資料筆數排序
    table_stats.sort(key=lambda x: x["row_count"], reverse=True)
    
    print("-" * 70)
    print(f"{'資料表名稱':<25} {'欄位數':<8} {'資料筆數':<12} {'百分比':<8}")
    print("-" * 70)
    
    for stat in table_stats:
        percentage = (stat["row_count"] / total_rows * 100) if total_rows > 0 else 0
        print(f"{stat['table_name']:<25} {stat['column_count']:<8} {stat['row_count']:<12} {percentage:>6.1f}%")
    
    print("-" * 70)
    print(f"{'總計':<25} {'-':<8} {total_rows:<12} {'100.0%':<8}")
    print()
    
    # 顯示外鍵關係
    print("=" * 70)
    print("外鍵關係")
    print("=" * 70)
    
    for table_name in table_names:
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print(f"\n{table_name}:")
            for fk in foreign_keys:
                cols = ", ".join(fk['constrained_columns'])
                ref_cols = ", ".join(fk['referred_columns'])
                ref_table = fk['referred_table']
                print(f"  - {cols} → {ref_table}.{ref_cols}")
    
    print()
    print("=" * 70)
    print("✓ 報告完成")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
