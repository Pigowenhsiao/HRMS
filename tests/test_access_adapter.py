import pytest
import os
from unittest.mock import patch, MagicMock
from hrms.core.db.adapters.access_adapter import AccessAdapter
from hrms.core.exceptions import DatabaseConnectionError, DuplicateRecordError

class TestAccessAdapter:
    """Access 適配器測試"""
    
    def setup_method(self):
        """測試前設置"""
        self.test_db_path = "test_hrms.mdb"
        # 確保測試資料庫不存在
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def teardown_method(self):
        """測試後清理"""
        # 刪除測試資料庫
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_initialization(self):
        """測試初始化"""
        adapter = AccessAdapter(self.test_db_path)
        assert adapter.db_path == self.test_db_path
        # 確保資料庫文件已創建
        assert os.path.exists(self.test_db_path)
    
    @patch('hrms.core.db.adapters.access_adapter.pyodbc')
    def test_connection_error(self, mock_pyodbc):
        """測試連接錯誤"""
        mock_pyodbc.connect.side_effect = Exception("Connection failed")
        
        with pytest.raises(DatabaseConnectionError):
            adapter = AccessAdapter(self.test_db_path)
            adapter.get_connection()
    
    def test_create_and_get_record(self):
        """測試創建和獲取記錄"""
        adapter = AccessAdapter(self.test_db_path)
        
        # 插入測試數據
        test_row = {
            "EMP_ID": "000001",
            "C_Name": "測試員工",
            "Active": True
        }
        
        result = adapter.upsert("Employees", "EMP_ID", test_row)
        assert result["EMP_ID"] == "000001"
        
        # 獲取記錄
        retrieved = adapter.get_by_pk("Employees", "EMP_ID", "000001")
        assert retrieved is not None
        assert retrieved["C_Name"] == "測試員工"
    
    def test_update_record(self):
        """測試更新記錄"""
        adapter = AccessAdapter(self.test_db_path)
        
        # 先插入記錄
        initial_row = {
            "EMP_ID": "000002",
            "C_Name": "初始員工",
            "Active": True
        }
        adapter.upsert("Employees", "EMP_ID", initial_row)
        
        # 更新記錄
        updated_row = {
            "EMP_ID": "000002",
            "C_Name": "更新員工",
            "Active": False
        }
        result = adapter.upsert("Employees", "EMP_ID", updated_row)
        assert result["C_Name"] == "更新員工"
        assert result["Active"] is False
        
        # 驗證更新結果
        retrieved = adapter.get_by_pk("Employees", "EMP_ID", "000002")
        assert retrieved["C_Name"] == "更新員工"
        assert retrieved["Active"] is False
    
    def test_delete_record(self):
        """測試刪除記錄"""
        adapter = AccessAdapter(self.test_db_path)
        
        # 插入記錄
        test_row = {
            "EMP_ID": "000003",
            "C_Name": "待刪員工",
            "Active": True
        }
        adapter.upsert("Employees", "EMP_ID", test_row)
        
        # 驗證記錄存在
        retrieved = adapter.get_by_pk("Employees", "EMP_ID", "000003")
        assert retrieved is not None
        
        # 刪除記錄
        result = adapter.delete("Employees", "EMP_ID", "000003")
        assert result is True
        
        # 驗證記錄已刪除
        retrieved = adapter.get_by_pk("Employees", "EMP_ID", "000003")
        assert retrieved is None
    
    def test_list_records(self):
        """測試列表記錄"""
        adapter = AccessAdapter(self.test_db_path)
        
        # 插入多筆測試數據
        test_data = [
            {"EMP_ID": "000004", "C_Name": "員工A", "Active": True},
            {"EMP_ID": "000005", "C_Name": "員工B", "Active": False},
            {"EMP_ID": "000006", "C_Name": "員工C", "Active": True}
        ]
        
        for row in test_data:
            adapter.upsert("Employees", "EMP_ID", row)
        
        # 獲取所有記錄
        all_records = adapter.list("Employees")
        assert len(all_records) >= 3  # 可能包含前面測試插入的記錄
        
        # 獲取過濾後的記錄
        active_records = adapter.list("Employees", filters={"Active": "true"})
        assert len([r for r in active_records if r["EMP_ID"] in ["000004", "000006"]]) >= 2
    
    def test_list_with_limit(self):
        """測試帶限制的列表"""
        adapter = AccessAdapter(self.test_db_path)
        
        # 插入多筆測試數據
        for i in range(10):
            test_row = {
                "EMP_ID": f"0000{i+10}",
                "C_Name": f"員工{i}",
                "Active": True
            }
            adapter.upsert("Employees", "EMP_ID", test_row)
        
        # 測試限制
        records = adapter.list("Employees", limit=5)
        assert len(records) <= 5
    
    def test_distinct_values(self):
        """測試獲取不重複值"""
        adapter = AccessAdapter(self.test_db_path)
        
        # 插入帶有相同和不同值的記錄
        test_data = [
            {"EMP_ID": "000020", "Area": "A1", "C_Name": "員工A"},
            {"EMP_ID": "000021", "Area": "A2", "C_Name": "員工B"},
            {"EMP_ID": "000022", "Area": "A1", "C_Name": "員工C"}
        ]
        
        for row in test_data:
            adapter.upsert("Employees", "EMP_ID", row)
        
        # 獲取不重複的區域值
        distinct_areas = adapter.list_distinct("Employees", "Area")
        assert "A1" in distinct_areas
        assert "A2" in distinct_areas
        assert len(distinct_areas) == 2