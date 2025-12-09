#!/usr/bin/env python3
"""
資料庫結構檢查腳本
檢查 SQLite 資料庫中的所有表格及其結構，並生成報告
"""

import sqlite3
import os
from datetime import datetime

# 設定資料庫路徑
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hrms.db')
REPORT_PATH = os.path.join(os.path.dirname(__file__), 'database_schema_report.txt')

def connect_to_database():
    """連接到 SQLite 資料庫"""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"資料庫連接失敗: {e}")
        return None

def get_all_tables(conn):
    """獲取所有表格名稱"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    return [table[0] for table in tables]

def get_table_info(conn, table_name):
    """獲取表格結構資訊"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    return columns

def get_table_row_count(conn, table_name):
    """獲取表格資料筆數"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    return count

def format_column_info(columns):
    """格式化欄位資訊"""
    if not columns:
        return "  無欄位資訊"
    
    lines = []
    lines.append("  {:<5} {:<20} {:<10} {:<8} {:<15} {}".format(
        "編號", "欄位名稱", "資料類型", "必填", "預設值", "主鍵"
    ))
    lines.append("  " + "-" * 80)
    
    for col in columns:
        cid, name, type_, notnull, dflt_value, pk = col
        notnull_str = "YES" if notnull else "NO"
        pk_str = "PK" if pk else ""
        dflt_str = str(dflt_value) if dflt_value is not None else ""
        
        lines.append("  {:<5} {:<20} {:<10} {:<8} {:<15} {}".format(
            cid, name, type_, notnull_str, dflt_str, pk_str
        ))
    
    return "\n".join(lines)

def generate_report():
    """生成完整的資料庫結構報告"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        # 獲取所有表格
        tables = get_all_tables(conn)
        
        if not tables:
            print("資料庫中沒有找到任何表格")
            return False
        
        # 開始生成報告內容
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("HRMS 資料庫結構報告")
        report_lines.append("=" * 80)
        report_lines.append(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"資料庫檔案: {DB_PATH}")
        report_lines.append(f"總表格數量: {len(tables)}")
        report_lines.append("")
        
        # 分隔線
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 遍歷每個表格
        empty_tables = []
        
        for i, table_name in enumerate(tables, 1):
            report_lines.append(f"【表格 {i}/{len(tables)}】 {table_name}")
            report_lines.append("-" * 80)
            
            # 獲取表格結構
            columns = get_table_info(conn, table_name)
            report_lines.append(format_column_info(columns))
            report_lines.append("")
            
            # 檢查資料筆數
            row_count = get_table_row_count(conn, table_name)
            report_lines.append(f"  資料筆數: {row_count:,} 筆")
            
            if row_count == 0:
                report_lines.append("  ⚠️  這是一個空表格（沒有資料）")
                empty_tables.append(table_name)
            
            report_lines.append("")
            report_lines.append("=" * 80)
            report_lines.append("")
        
        # 總結
        report_lines.append("📊 總結報告")
        report_lines.append("=" * 80)
        report_lines.append(f"總共檢查了 {len(tables)} 個表格")
        report_lines.append(f"空表格數量: {len(empty_tables)} 個")
        
        if empty_tables:
            report_lines.append(f"空表格清單: {', '.join(empty_tables)}")
        else:
            report_lines.append("所有表格都包含資料 ✓")
        
        report_lines.append("")
        report_lines.append("報告生成完成！")
        
        # 將報告寫入檔案
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        # 同時在螢幕上顯示
        print('\n'.join(report_lines))
        
        print(f"\n✅ 報告已保存到: {REPORT_PATH}")
        return True
        
    except sqlite3.Error as e:
        print(f"資料庫操作錯誤: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("開始檢查資料庫結構...")
    generate_report()
