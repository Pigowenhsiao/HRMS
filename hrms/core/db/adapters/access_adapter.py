from __future__ import annotations
from typing import Dict, List, Optional
from pathlib import Path
import pyodbc
from ..database import DBAdapter

class AccessAdapter(DBAdapter):
    """
    Access 資料庫適配器
    使用 pyodbc 與 Access 資料庫進行交互
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection_string = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        self._create_database_if_not_exists()

    def _create_database_if_not_exists(self):
        """
        如果資料庫不存在，則創建資料庫和基本表格
        """
        import os
        if not os.path.exists(self.db_path):
            # 建立資料庫檔案 - 通常使用空的 Access 檔案作為模板
            # 這裡我們會先創建一個空白的 mdb 檔案
            import subprocess
            try:
                # 嘗試使用 mdb-export 工具（如果安裝了 mdbtools）
                subprocess.run(["mdb-export", self.db_path], capture_output=True)
            except FileNotFoundError:
                # 如果沒有安裝 mdbtools，則創建一個新的空文件
                Path(self.db_path).touch()
        
        # 確保必要的表格存在
        self._create_tables_if_not_exists()

    def _create_tables_if_not_exists(self):
        """
        創建必要的表格（如果不存在）
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 創建 Employees 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Employees (
                    EMP_ID VARCHAR(10) PRIMARY KEY,
                    Dept_Code VARCHAR(10),
                    C_Name VARCHAR(50),
                    Title VARCHAR(50),
                    On_Board_Date DATETIME,
                    Shift VARCHAR(10),
                    Area VARCHAR(10),
                    Function VARCHAR(20),
                    Meno VARCHAR(255),
                    Active BOOLEAN,
                    VAC_ID VARCHAR(10),
                    VAC_DESC VARCHAR(100),
                    Start_date DATETIME,
                    End_date DATETIME,
                    AreaDate DATETIME
                )
            """)

            # 創建 Departments 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Departments (
                    Dept_Code VARCHAR(10) PRIMARY KEY,
                    Dept_Name VARCHAR(50),
                    Dept_Desc VARCHAR(255),
                    Supervisor VARCHAR(50)
                )
            """)

            # 創建 Areas 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Areas (
                    Area VARCHAR(10) PRIMARY KEY,
                    Area_Desc VARCHAR(100),
                    Active BOOLEAN
                )
            """)

            # 創建 JobTypes 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS JobTypes (
                    Job_Code VARCHAR(10) PRIMARY KEY,
                    Job_Desc VARCHAR(100)
                )
            """)

            # 創建 VacationTypes 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS VacationTypes (
                    VAC_ID VARCHAR(10) PRIMARY KEY,
                    VAC_DESC VARCHAR(100),
                    Active BOOLEAN
                )
            """)

            # 創建 Authorities 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Authorities (
                    Account VARCHAR(50) PRIMARY KEY,
                    Auth_Type VARCHAR(10),
                    Active BOOLEAN
                )
            """)

            conn.commit()

    def get_connection(self):
        """
        獲取資料庫連接
        """
        return pyodbc.connect(self.connection_string)

    def list(self, table: str, filters: Optional[Dict[str, str]] = None, limit: Optional[int] = None) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 準備查詢語句
            query = f"SELECT * FROM [{table}]"
            params = []
            
            # 添加過濾條件
            if filters:
                conditions = []
                for k, v in filters.items():
                    conditions.append(f"[{k}] = ?")
                    params.append(v)
                query += " WHERE " + " AND ".join(conditions)
            
            # 添加限制條件
            if limit is not None:
                # Access 中的 TOP 語法用於限制結果數量
                query = query.replace("SELECT *", f"SELECT TOP {limit} *")
            
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return result

    def get_by_pk(self, table: str, pk: str, value: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM [{table}] WHERE [{pk}] = ?"
            cursor.execute(query, value)
            row = cursor.fetchone()
            
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            
            return None

    def upsert(self, table: str, pk: str, row: Dict) -> Dict:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 檢查記錄是否已存在
            check_query = f"SELECT COUNT(*) FROM [{table}] WHERE [{pk}] = ?"
            cursor.execute(check_query, row[pk])
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # 更新記錄
                set_parts = [f"[{k}] = ?" for k in row.keys()]
                set_clause = ", ".join(set_parts)
                query = f"UPDATE [{table}] SET {set_clause} WHERE [{pk}] = ?"
                params = list(row.values()) + [row[pk]]
                cursor.execute(query, params)
            else:
                # 插入新記錄
                columns = ", ".join([f"[{k}]" for k in row.keys()])
                placeholders = ", ".join(["?" for _ in row.keys()])
                query = f"INSERT INTO [{table}] ({columns}) VALUES ({placeholders})"
                cursor.execute(query, list(row.values()))
            
            conn.commit()
            return row

    def delete(self, table: str, pk: str, value: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"DELETE FROM [{table}] WHERE [{pk}] = ?"
            cursor.execute(query, value)
            conn.commit()
            
            # 檢查是否有記錄被刪除
            return cursor.rowcount > 0

    def list_distinct(self, table: str, column: str) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"SELECT DISTINCT [{column}] FROM [{table}] WHERE [{column}] IS NOT NULL"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [row[0] for row in rows if row[0] is not None]