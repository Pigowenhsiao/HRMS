import pytest
from datetime import datetime
from hrms.core.utils.date_utils import parse_date, format_date, validate_date_range, is_valid_date_format, calculate_date_difference

class TestDateUtils:
    """日期處理工具測試類別"""
    
    def test_parse_date(self):
        """測試日期解析功能"""
        # 測試不同格式的日期
        assert parse_date("2023-01-15") == datetime(2023, 1, 15)
        assert parse_date("2023/01/15") == datetime(2023, 1, 15)
        assert parse_date("2023-01-15 14:30:00") == datetime(2023, 1, 15, 14, 30, 0)
        assert parse_date("2023/01/15 14:30:00") == datetime(2023, 1, 15, 14, 30, 0)
        
        # 測試空值
        assert parse_date(None) is None
        assert parse_date("") is None
        assert parse_date("   ") is None
        
        # 測試無效格式
        assert parse_date("invalid-date") is None
    
    def test_format_date(self):
        """測試日期格式化功能"""
        dt = datetime(2023, 1, 15)
        
        # 測試 datetime 物件格式化
        assert format_date(dt, "%Y-%m-%d") == "2023-01-15"
        assert format_date(dt, "%Y/%m/%d") == "2023/01/15"
        
        # 測試日期字串格式化
        assert format_date("2023-01-15", "%Y年%m月%d日") == "2023年01月15日"
        
        # 測試空值
        assert format_date(None) is None
        
        # 測試無效格式的字串
        assert format_date("invalid-date") is None
    
    def test_validate_date_range(self):
        """測試日期範圍驗證"""
        # 測試有效範圍
        assert validate_date_range("2023-01-01", "2023-12-31") is True
        
        # 測試相同日期
        assert validate_date_range("2023-06-15", "2023-06-15") is True
        
        # 測試無效範圍（開始日期在結束日期之後）
        assert validate_date_range("2023-12-31", "2023-01-01") is False
        
        # 測試單一空值
        assert validate_date_range(None, "2023-12-31") is True
        assert validate_date_range("2023-01-01", None) is True
    
    def test_is_valid_date_format(self):
        """測試日期格式驗證"""
        # 測試有效格式
        assert is_valid_date_format("2023-01-15") is True
        assert is_valid_date_format("2023/01/15") is True
        assert is_valid_date_format("2023-01-15 14:30:00") is True
        assert is_valid_date_format("2023/01/15 14:30:00") is True
        
        # 測試無效格式
        assert is_valid_date_format("15-01-2023") is False
        assert is_valid_date_format("invalid-date") is False
        
        # 測試空值
        assert is_valid_date_format("") is False
        assert is_valid_date_format(None) is False
    
    def test_calculate_date_difference(self):
        """測試日期差異計算"""
        # 測試正差異
        assert calculate_date_difference("2023-01-01", "2023-01-10") == 9
        
        # 測試負差異
        assert calculate_date_difference("2023-01-10", "2023-01-01") == -9
        
        # 測試同一天
        assert calculate_date_difference("2023-01-01", "2023-01-01") == 0
        
        # 測試無效日期
        assert calculate_date_difference("invalid", "2023-01-10") is None
        assert calculate_date_difference("2023-01-01", "invalid") is None