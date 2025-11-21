"""
自定義異常類別
"""
class HRMSException(Exception):
    """HRMS 系統基本異常類別"""
    pass

class DatabaseConnectionError(HRMSException):
    """資料庫連接錯誤"""
    pass

class DataValidationError(HRMSException):
    """數據驗證錯誤"""
    pass

class RecordNotFoundError(HRMSException):
    """記錄找不到錯誤"""
    pass

class DuplicateRecordError(HRMSException):
    """重複記錄錯誤"""
    pass

class InvalidOperationError(HRMSException):
    """無效操作錯誤"""
    pass

class AuthorizationError(HRMSException):
    """授權錯誤"""
    pass

class ConfigurationError(HRMSException):
    """配置錯誤"""
    pass