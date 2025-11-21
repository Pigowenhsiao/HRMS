"""
日誌記錄工具函數
"""
import logging
from pathlib import Path
import sys
from datetime import datetime

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    設置日誌記錄器
    
    Args:
        name: 記錄器名稱
        log_file: 日誌文件路徑 (可選)
        level: 日誌級別
        
    Returns:
        配置好的 Logger 實例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重複添加處理器
    if logger.handlers:
        return logger

    # 設置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件處理器 (可選)
    if log_file:
        # 確保日誌目錄存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# 預設日誌記錄器
app_logger = setup_logger("HRMS", "logs/hrms.log")

def log_info(message: str):
    """記錄信息級別日誌"""
    app_logger.info(message)

def log_warning(message: str):
    """記錄警告級別日誌"""
    app_logger.warning(message)

def log_error(message: str):
    """記錄錯誤級別日誌"""
    app_logger.error(message)

def log_exception(message: str = ""):
    """記錄異常信息"""
    if message:
        app_logger.exception(message)
    else:
        app_logger.exception("發生異常")