import pytest
from unittest.mock import patch, MagicMock
from hrms.persons.service import list_employees, get_employee, upsert_employee, delete_employee
from hrms.core.models import EmployeeCreate, EmployeeUpdate
from hrms.core.exceptions import DataValidationError, RecordNotFoundError

class TestEmployeeService:
    """員工服務測試類別"""
    
    @patch('hrms.persons.service.get_employee')
    @patch('hrms.core.db.unit_of_work.UnitOfWork')
    def test_upsert_employee_create(self, mock_uow, mock_get_employee):
        """測試創建員工"""
        # 模擬員工不存在
        mock_get_employee.return_value = None
        
        mock_repo = MagicMock()
        mock_uow.from_settings.return_value.__enter__.return_value.adapter = MagicMock()
        
        row = {
            "EMP_ID": "000001",
            "C_Name": "測試員工",
            "Active": True
        }
        
        # 測試創建員工
        upsert_employee(row)
        
        # 驗證是否調用了正確的適配器方法
        assert mock_uow.from_settings.return_value.__enter__.return_value.adapter.upsert.called

    @patch('hrms.persons.service.get_employee')
    @patch('hrms.core.db.unit_of_work.UnitOfWork')
    def test_upsert_employee_update(self, mock_uow, mock_get_employee):
        """測試更新員工"""
        # 模擬員工已存在
        mock_get_employee.return_value = {"EMP_ID": "000001"}
        
        mock_repo = MagicMock()
        mock_uow.from_settings.return_value.__enter__.return_value.adapter = MagicMock()
        
        row = {
            "EMP_ID": "000001",
            "C_Name": "已更新員工",
            "Active": True
        }
        
        # 測試更新員工
        upsert_employee(row)
        
        # 驗證是否調用了正確的適配器方法
        assert mock_uow.from_settings.return_value.__enter__.return_value.adapter.upsert.called

    def test_employee_create_validation(self):
        """測試員工創建模型驗證"""
        # 測試有效數據
        valid_employee = EmployeeCreate(
            EMP_ID="000001",
            C_Name="測試員工",
            Active=True
        )
        assert valid_employee.EMP_ID == "000001"
        
        # 測試無效數據（短於4位的員工編號）
        with pytest.raises(ValueError):
            EmployeeCreate(
                EMP_ID="01",  # 長度小於4
                C_Name="測試員工",
                Active=True
            )

    def test_employee_update_validation(self):
        """測試員工更新模型驗證"""
        # 測試有效數據
        valid_employee = EmployeeUpdate(
            EMP_ID="000001",
            C_Name="測試員工",
            Active=True
        )
        assert valid_employee.EMP_ID == "000001"
        
        # 測試可選字段
        valid_employee_optional = EmployeeUpdate(EMP_ID="000002")
        assert valid_employee_optional.EMP_ID == "000002"
        assert valid_employee_optional.C_Name is None