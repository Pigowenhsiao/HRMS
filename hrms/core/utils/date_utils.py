"""
日期處理工具函數
"""
from datetime import datetime
from typing import Optional, Union
import re

def parse_date(date_str: Optional[str], formats: Optional[list] = None) -> Optional[datetime]:
    """
    解析多種格式的日期字串
    
    Args:
        date_str: 日期字串
        formats: 日期格式列表，預設為常見格式
        
    Returns:
        解析後的 datetime 物件，如果無法解析則返回 None
    """
    if not date_str or not isinstance(date_str, str) or date_str.strip() == '':
        return None
    
    if formats is None:
        formats = [
            "%Y-%m-%d",      # 2023-01-15
            "%Y/%m/%d",      # 2023/01/15
            "%Y-%m-%d %H:%M:%S",  # 2023-01-15 14:30:00
            "%Y/%m/%d %H:%M:%S",  # 2023/01/15 14:30:00
            "%Y年%m月%d日",   # 2023年01月15日
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    # 如果所有格式都無法解析，則返回 None
    return None

def format_date(date_obj: Optional[Union[datetime, str]], output_format: str = "%Y-%m-%d") -> Optional[str]:
    """
    將日期物件或日期字串格式化為指定格式
    
    Args:
        date_obj: datetime 物件或日期字串
        output_format: 輸出格式
        
    Returns:
        格式化後的日期字串，如果無法解析則返回 None
    """
    if date_obj is None:
        return None
    
    if isinstance(date_obj, str):
        # 如果輸入是字串，先解析為 datetime 物件
        parsed_date = parse_date(date_obj)
        if parsed_date is None:
            return None
        date_obj = parsed_date
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime(output_format)
    
    return None

def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> bool:
    """
    驗證日期範圍的有效性
    
    Args:
        start_date: 開始日期
        end_date: 結束日期
        
    Returns:
        如果日期範圍有效則返回 True，否則返回 False
    """
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)
    
    if start_dt and end_dt:
        return start_dt <= end_dt
    
    # 如果其中一個日期為空，我們認為日期範圍是有效的
    return True

def is_valid_date_format(date_str: str, format_patterns: Optional[list] = None) -> bool:
    """
    檢查日期字串是否符合指定的格式模式
    
    Args:
        date_str: 日期字串
        format_patterns: 要檢查的格式模式列表 (正規表達式)
        
    Returns:
        如果符合任意格式則返回 True，否則返回 False
    """
    if not date_str:
        return False
    
    if format_patterns is None:
        format_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',      # YYYY-MM-DD
            r'^\d{4}/\d{2}/\d{2}$',      # YYYY/MM/DD
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',  # YYYY-MM-DD HH:MM:SS
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$',  # YYYY/MM/DD HH:MM:SS
            r'^\d{4}年\d{2}月\d{2}日$',   # YYYY年MM月DD日
        ]
    
    for pattern in format_patterns:
        if re.match(pattern, date_str.strip()):
            return True
    
    return False

def calculate_date_difference(start_date: str, end_date: str) -> Optional[int]:
    """
    計算兩個日期之間的天數差異
    
    Args:
        start_date: 開始日期
        end_date: 結束日期
        
    Returns:
        兩日期間的天數差異，如果日期無法解析則返回 None
    """
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)
    
    if start_dt and end_dt:
        diff = end_dt - start_dt
        return diff.days
    
    return None