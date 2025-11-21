"""
CSV 資料遷移至 Access 資料庫的工具函數
"""
from pathlib import Path
import pandas as pd
import sys
from typing import Dict, List

def migrate_csv_to_access(data_dir: str = "./data", access_db_path: str = "./hrms.mdb"):
    """
    將 CSV 檔案中的資料遷移到 Access 資料庫
    """
    try:
        from hrms.core.db.adapters.access_adapter import AccessAdapter
    except ImportError as e:
        print(f"無法導入 Access 適配器: {e}")
        print("請確保已安裝 pyodbc 並在 Windows 系統上安裝 Microsoft Access Database Engine")
        return

    try:
        # 建立 Access 適配器
        adapter = AccessAdapter(access_db_path)
    except Exception as e:
        print(f"無法建立 Access 適配器: {e}")
        print("請確保您的系統已安裝 Microsoft Access 驅動程式 (僅 Windows 支援)")
        return

    # 定義需要遷移的檔案及其對應的表格名稱
    csv_to_table_mapping = {
        "BASIC.csv": "Employees",
        "L_Section.csv": "Departments",
        "Area.csv": "Areas",
        "L_Job.csv": "JobTypes",
        "VAC_Type.csv": "VacationTypes",
        "Authority.csv": "Authorities"
    }

    # 遍歷所有 CSV 檔案並遷移到 Access
    for csv_filename, table_name in csv_to_table_mapping.items():
        csv_path = Path(data_dir) / csv_filename

        if csv_path.exists():
            print(f"正在遷移 {csv_filename} 到 {table_name} 表格...")

            # 讀取 CSV 檔案
            df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)

            # 處理特定欄位的資料類型轉換
            if table_name == "Employees":
                # 處理日期欄位
                date_columns = ['On_Board_Date', 'Start_date', 'End_date', 'AreaDate']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = df[col].replace('', None)

                # 處理布林欄位
                if 'Active' in df.columns:
                    df['Active'] = df['Active'].apply(lambda x: x.lower() == 'true' if pd.notna(x) else None)

            elif table_name in ['Areas', 'VacationTypes', 'Authorities']:
                # 處理布林欄位
                if 'Active' in df.columns:
                    df['Active'] = df['Active'].apply(lambda x: x.lower() == 'true' if pd.notna(x) else None)

            # 將資料插入到 Access 表格中
            try:
                with adapter.get_connection() as conn:
                    cursor = conn.cursor()

                    # 檢查表格是否為空，如果為空則插入所有記錄
                    check_query = f"SELECT COUNT(*) FROM [{table_name}]"
                    cursor.execute(check_query)
                    count = cursor.fetchone()[0]

                    if count == 0:
                        # 表格為空，插入所有記錄
                        for _, row in df.iterrows():
                            # 準備插入語句
                            columns = ", ".join([f"[{col}]" for col in df.columns])
                            placeholders = ", ".join(["?" for _ in df.columns])
                            insert_query = f"INSERT INTO [{table_name}] ({columns}) VALUES ({placeholders})"

                            # 處理行中的 None 值
                            row_values = []
                            for val in row.values:
                                if pd.isna(val) or val == '':
                                    row_values.append(None)
                                else:
                                    row_values.append(val)

                            cursor.execute(insert_query, row_values)

                        conn.commit()
                        print(f"成功遷移 {len(df)} 筆 {csv_filename} 記錄到 {table_name} 表格")
                    else:
                        print(f"{table_name} 表格已有資料，跳過遷移")
            except Exception as e:
                print(f"插入 {table_name} 表格時發生錯誤: {e}")
        else:
            print(f"警告: 找不到檔案 {csv_path}，跳過遷移")

def verify_migration(access_db_path: str = "./hrms.mdb"):
    """
    驗證遷移後的資料完整性
    """
    try:
        from hrms.core.db.adapters.access_adapter import AccessAdapter
    except ImportError as e:
        print(f"無法導入 Access 適配器: {e}")
        return

    try:
        adapter = AccessAdapter(access_db_path)
    except Exception as e:
        print(f"無法建立 Access 適配器進行驗證: {e}")
        return

    tables_to_check = ["Employees", "Departments", "Areas", "JobTypes", "VacationTypes", "Authorities"]

    print("開始驗證遷移後的資料...")

    for table_name in tables_to_check:
        try:
            # 獲取表格記錄數
            records = adapter.list(table_name)
            print(f"{table_name}: {len(records)} 筆記錄")

            # 顯示前幾筆記錄以供檢查
            if records:
                print(f"  - 範例記錄: {records[0]}")
        except Exception as e:
            print(f"檢查 {table_name} 時發生錯誤: {e}")

if __name__ == "__main__":
    # 運行遷移工具
    print("開始進行 CSV 到 Access 的數據遷移...")
    print("注意: 此功能僅在安裝了 Microsoft Access 驅動程式的 Windows 系統上可用")
    migrate_csv_to_access()

    # 驗證遷移結果
    verify_migration()