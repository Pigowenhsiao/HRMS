import pytest
import os
import tempfile
from pathlib import Path
from hrms.core.db.adapters.csv_adapter import CSVAdapter
from hrms.core.exceptions import DatabaseConnectionError

class TestCSVAdapter:
    """CSV 適配器測試"""
    
    def setup_method(self):
        """測試前設置"""
        # 創建臨時目錄
        self.temp_dir = tempfile.mkdtemp()
        self.csv_adapter = CSVAdapter(self.temp_dir)
    
    def teardown_method(self):
        """測試後清理"""
        # 刪除臨時目錄及其內容
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """測試初始化"""
        assert Path(self.temp_dir).exists()
        assert self.csv_adapter.data_dir == Path(self.temp_dir)
    
    def test_csv_path(self):
        """測試 CSV 文件路徑生成"""
        path = self.csv_adapter._csv_path("test_table")
        expected = Path(self.temp_dir) / "TEST_TABLE.csv"
        assert path == expected
    
    def test_ensure_exists(self):
        """測試確保文件存在"""
        table_name = "test_table"
        self.csv_adapter._ensure_exists(table_name)
        
        csv_file = self.temp_dir / f"{table_name.upper()}.csv"
        assert csv_file.exists()
    
    def test_upsert_and_get(self):
        """測試插入和獲取記錄"""
        table_name = "test_employees"
        test_row = {
            "EMP_ID": "000001",
            "C_Name": "測試員工",
            "Active": "true"
        }
        
        # 插入記錄
        result = self.csv_adapter.upsert(table_name, "EMP_ID", test_row)
        assert result["EMP_ID"] == "000001"
        
        # 獲取記錄
        retrieved = self.csv_adapter.get_by_pk(table_name, "EMP_ID", "000001")
        assert retrieved is not None
        assert retrieved["C_Name"] == "測試員工"
    
    def test_update_record(self):
        """測試更新記錄"""
        table_name = "test_employees"
        
        # 插入初始記錄
        initial_row = {
            "EMP_ID": "000002",
            "C_Name": "初始員工",
            "Active": "true"
        }
        self.csv_adapter.upsert(table_name, "EMP_ID", initial_row)
        
        # 更新記錄
        updated_row = {
            "EMP_ID": "000002",
            "C_Name": "更新員工",
            "Active": "false"
        }
        result = self.csv_adapter.upsert(table_name, "EMP_ID", updated_row)
        assert result["C_Name"] == "更新員工"
        
        # 驗證更新結果
        retrieved = self.csv_adapter.get_by_pk(table_name, "EMP_ID", "000002")
        assert retrieved["C_Name"] == "更新員工"
        assert retrieved["Active"] == "false"
    
    def test_delete_record(self):
        """測試刪除記錄"""
        table_name = "test_employees"
        
        # 插入記錄
        test_row = {
            "EMP_ID": "000003",
            "C_Name": "待刪員工",
            "Active": "true"
        }
        self.csv_adapter.upsert(table_name, "EMP_ID", test_row)
        
        # 驗證記錄存在
        retrieved = self.csv_adapter.get_by_pk(table_name, "EMP_ID", "000003")
        assert retrieved is not None
        
        # 刪除記錄
        result = self.csv_adapter.delete(table_name, "EMP_ID", "000003")
        assert result is True
        
        # 驗證記錄已刪除
        retrieved = self.csv_adapter.get_by_pk(table_name, "EMP_ID", "000003")
        assert retrieved is None
    
    def test_list_records(self):
        """測試列表記錄"""
        table_name = "test_employees"
        
        # 插入多筆測試數據
        test_data = [
            {"EMP_ID": "000004", "C_Name": "員工A", "Active": "true"},
            {"EMP_ID": "000005", "C_Name": "員工B", "Active": "false"},
            {"EMP_ID": "000006", "C_Name": "員工C", "Active": "true"}
        ]
        
        for row in test_data:
            self.csv_adapter.upsert(table_name, "EMP_ID", row)
        
        # 獲取所有記錄
        all_records = self.csv_adapter.list(table_name)
        assert len([r for r in all_records if r["EMP_ID"] in ["000004", "000005", "000006"]]) >= 3
        
        # 獲取過濾後的記錄
        active_records = self.csv_adapter.list(table_name, filters={"Active": "true"})
        active_test_records = [r for r in active_records if r["EMP_ID"] in ["000004", "000006"]]
        assert len(active_test_records) >= 2
    
    def test_list_with_limit(self):
        """測試帶限制的列表"""
        table_name = "test_employees"
        
        # 插入多筆測試數據
        for i in range(10):
            test_row = {
                "EMP_ID": f"0000{i+10}",
                "C_Name": f"員工{i}",
                "Active": "true"
            }
            self.csv_adapter.upsert(table_name, "EMP_ID", test_row)
        
        # 測試限制
        records = self.csv_adapter.list(table_name, limit=5)
        assert len(records) <= 5
    
    def test_distinct_values(self):
        """測試獲取不重複值"""
        table_name = "test_employees"
        
        # 插入帶有相同和不同值的記錄
        test_data = [
            {"EMP_ID": "000020", "Area": "A1", "C_Name": "員工A"},
            {"EMP_ID": "000021", "Area": "A2", "C_Name": "員工B"},
            {"EMP_ID": "000022", "Area": "A1", "C_Name": "員工C"}
        ]
        
        for row in test_data:
            self.csv_adapter.upsert(table_name, "EMP_ID", row)
        
        # 獲取不重複的區域值
        distinct_areas = self.csv_adapter.list_distinct(table_name, "Area")
        assert "A1" in distinct_areas
        assert "A2" in distinct_areas
        assert len(distinct_areas) == 2