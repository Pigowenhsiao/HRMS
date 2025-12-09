#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 Access 資料庫結構
產生資料表清單、欄位資訊、主鍵、索引等
"""
import pyodbc
import pandas as pd
from pathlib import Path
import json

ACCESS_DB_PATH = "/home/pigo/Documents/python/HRMS/data/HRMS.mdb"
OUTPUT_DIR = "/home/pigo/Documents/python/HRMS/data/analysis"

def connect_access():
    """連接 Access 資料庫"""
    driver = "{Microsoft Access Driver (*.mdb, *.accdb)}"
    conn_str = f"DRIVER={driver};DBQ={ACCESS_DB_PATH};"
    return pyodbc.connect(conn_str)

def list_tables(conn):
    """列出所有使用者資料表（排除系統表）"""
    cursor = conn.cursor()
    tables = []
    for row in cursor.tables(tableType="TABLE"):
        table_name = row.table_name
        if not table_name.startswith("MSys") and not table_name.startswith("~"):
            tables.append(table_name)
    return sorted(tables)

def analyze_table_structure(conn, table_name):
    """分析單一資料表結構"""
    cursor = conn.cursor()
    
    # 取得欄位資訊
    cursor.execute(f"SELECT * FROM [{table_name}] WHERE 1=0")
    columns = []
    for col in cursor.description:
        columns.append({
            "name": col[0],
            "type": col[1].__name__,
            "size": col[3],
            "nullable": bool(col[6]),
            "precision": col[4],
            "scale": col[5]
        })
    
    # 取得資料筆數
    cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
    row_count = cursor.fetchone()[0]
    
    # 嘗試取得主鍵資訊（Access ODBC 支援有限）
    primary_keys = []
    try:
        for row in cursor.statistics(table=table_name):
            if row[5] == True:  # 是否為主鍵
                primary_keys.append(row[8])  # 欄位名稱
    except:
        pass
    
    # 取得索引資訊
    indexes = []
    try:
        for row in cursor.statistics(table=table_name):
            if row[5] == False and row[7] is not None:  # 排除主鍵，且有索引名稱
                indexes.append({
                    "name": row[7],
                    "column": row[8],
                    "unique": not bool(row[3])
                })
    except:
        pass
    
    # 取得範例資料（前 3 筆）
    sample_data = []
    if row_count > 0:
        try:
            df = pd.read_sql(f"SELECT TOP 3 * FROM [{table_name}]", conn)
            sample_data = df.fillna("").to_dict(orient="records")
        except:
            pass
    
    return {
        "table_name": table_name,
        "row_count": row_count,
        "columns": columns,
        "primary_keys": primary_keys,
        "indexes": indexes,
        "sample_data": sample_data
    }

def generate_sqlite_schema(table_info):
    """產生 SQLite 建表 SQL"""
    sql_parts = []
    foreign_keys = []
    
    for col in table_info["columns"]:
        col_name = col["name"]
        # 簡化的型別對映
        if "VARCHAR" in col["type"] or "TEXT" in col["type"]:
            data_type = "TEXT"
        elif "INT" in col["type"]:
            data_type = "INTEGER"
        elif "DOUBLE" in col["type"] or "FLOAT" in col["type"]:
            data_type = "REAL"
        elif "DATE" in col["type"] or "TIME" in col["type"]:
            data_type = "TEXT"  # SQLite 建議日期用 TEXT
        else:
            data_type = "TEXT"
        
        nullable = "NOT NULL" if not col["nullable"] else ""
        sql_parts.append(f'"{col_name}" {data_type} {nullable}')
    
    # 主鍵
    if table_info["primary_keys"]:
        pk_cols = ", ".join([f'"{pk}"' for pk in table_info["primary_keys"]])
        sql_parts.append(f"PRIMARY KEY ({pk_cols})")
    
    table_sql = f"CREATE TABLE IF NOT EXISTS \"{table_info['table_name']}\" (\n  " + ",\n  ".join(sql_parts) + "\n);"
    
    return table_sql

def main():
    """主函式"""
    print("=" * 60)
    print("分析 Access 資料庫結構")
    print("=" * 60)
    
    try:
        conn = connect_access()
        print(f"✓ 成功連接: {ACCESS_DB_PATH}")
        
        # 列出所有資料表
        tables = list_tables(conn)
        print(f"\n找到 {len(tables)} 個資料表")
        
        # 分析每個資料表
        analysis_result = {}
        for table_name in tables:
            print(f"\n分析資料表: {table_name}...")
            try:
                table_info = analyze_table_structure(conn, table_name)
                analysis_result[table_name] = table_info
                print(f"  - 欄位數: {len(table_info['columns'])}")
                print(f"  - 資料筆數: {table_info['row_count']}")
                print(f"  - 主鍵: {table_info['primary_keys']}")
                print(f"  - 索引數: {len(table_info['indexes'])}")
            except Exception as e:
                print(f"  ✗ 分析失敗: {e}")
        
        # 建立輸出目錄
        Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        
        # 儲存分析結果
        analysis_file = Path(OUTPUT_DIR) / "access_analysis.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 分析結果已儲存: {analysis_file}")
        
        # 產生 SQLite 建表 SQL
        sqlite_sql = []
        for table_name, table_info in analysis_result.items():
            sqlite_sql.append(f"-- Table: {table_name}")
            sqlite_sql.append(generate_sqlite_schema(table_info))
            sqlite_sql.append("")
        
        schema_file = Path(OUTPUT_DIR) / "sqlite_schema.sql"
        with open(schema_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sqlite_sql))
        print(f"✓ SQLite 建表 SQL 已產生: {schema_file}")
        
        # 產生資料表摘要報告
        summary = []
        summary.append("# Access 資料庫分析報告\n")
        summary.append(f"資料庫檔案: {ACCESS_DB_PATH}\n")
        summary.append(f"資料表總數: {len(tables)}\n")
        summary.append("## 資料表清單\n")
        
        for table_name, table_info in analysis_result.items():
            summary.append(f"### {table_name}\n")
            summary.append(f"- **資料筆數**: {table_info['row_count']}\n")
            summary.append(f"- **欄位數**: {len(table_info['columns'])}\n")
            summary.append(f"- **主鍵**: {', '.join(table_info['primary_keys']) if table_info['primary_keys'] else '無'}\n")
            summary.append(f"- **索引數**: {len(table_info['indexes'])}\n")
            summary.append("#### 欄位清單\n")
            summary.append("| 欄位名稱 | 型別 | 可空 | 長度 |\n")
            summary.append("|---------|------|------|------|\n")
            for col in table_info['columns']:
                summary.append(f"| {col['name']} | {col['type']} | {col['nullable']} | {col['size']} |\n")
            summary.append("\n")
        
        report_file = Path(OUTPUT_DIR) / "analysis_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.writelines(summary)
        print(f"✓ 分析報告已產生: {report_file}")
        
        conn.close()
        print("\n" + "=" * 60)
        print("分析完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        print("請確認已安裝 pyodbc 和 Access ODBC Driver")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
