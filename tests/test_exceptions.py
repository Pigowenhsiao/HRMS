import pytest
from hrms.core.exceptions import HRMSException, DatabaseConnectionError, DataValidationError, RecordNotFoundError, DuplicateRecordError, InvalidOperationError, AuthorizationError, ConfigurationError

class TestExceptions:
    """異常類別測試"""
    
    def test_hrms_exception(self):
        """測試基本異常類別"""
        with pytest.raises(HRMSException):
            raise HRMSException("測試基本異常")
    
    def test_database_connection_error(self):
        """測試資料庫連接錯誤"""
        with pytest.raises(DatabaseConnectionError):
            raise DatabaseConnectionError("測試資料庫連接錯誤")
    
    def test_data_validation_error(self):
        """測試數據驗證錯誤"""
        with pytest.raises(DataValidationError):
            raise DataValidationError("測試數據驗證錯誤")
    
    def test_record_not_found_error(self):
        """測試記錄找不到錯誤"""
        with pytest.raises(RecordNotFoundError):
            raise RecordNotFoundError("測試記錄找不到錯誤")
    
    def test_duplicate_record_error(self):
        """測試重複記錄錯誤"""
        with pytest.raises(DuplicateRecordError):
            raise DuplicateRecordError("測試重複記錄錯誤")
    
    def test_invalid_operation_error(self):
        """測試無效操作錯誤"""
        with pytest.raises(InvalidOperationError):
            raise InvalidOperationError("測試無效操作錯誤")
    
    def test_authorization_error(self):
        """測試授權錯誤"""
        with pytest.raises(AuthorizationError):
            raise AuthorizationError("測試授權錯誤")
    
    def test_configuration_error(self):
        """測試配置錯誤"""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("測試配置錯誤")
    
    def test_exception_inheritance(self):
        """測試異常繼承關係"""
        # 所有自定義異常都應該繼承自 HRMSException
        errors = [
            DatabaseConnectionError,
            DataValidationError,
            RecordNotFoundError,
            DuplicateRecordError,
            InvalidOperationError,
            AuthorizationError,
            ConfigurationError
        ]
        
        for error_class in errors:
            assert issubclass(error_class, HRMSException)