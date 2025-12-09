"""
HRMS 資料模型
包含所有 SQLAlchemy ORM 模型
"""

from .base import Base
from .employee import Basic, PersonInfo
from .section import Section, Area, Job, VacType, Shift, Shop
from .certification import (
    Certify, CertifyType, CertifyItem, TrainingRecord, 
    CertifyRecord, CertifyToolMap, MustTool, Software
)
from .authority import Authority, DelAuthority

# 所有模型列表
__all__ = [
    # Base
    "Base",
    
    # 員工相關
    "Basic",
    "PersonInfo",
    
    # 對照表
    "Section",
    "Area",
    "Job",
    "VacType",
    "Shift",
    "Shop",
    
    # 證照與訓練
    "Certify",
    "CertifyType",
    "CertifyItem",
    "TrainingRecord",
    "CertifyRecord",
    "CertifyToolMap",
    "MustTool",
    "Software",
    
    # 權限
    "Authority",
    "DelAuthority",
]

def create_all_tables(engine):
    """
    建立所有資料表
    """
    Base.metadata.create_all(engine)

def drop_all_tables(engine):
    """
    刪除所有資料表（慎用！）
    """
    Base.metadata.drop_all(engine)

def get_table_names():
    """
    取得所有資料表名稱
    """
    return [table.name for table in Base.metadata.sorted_tables]

def get_table_summary(engine):
    """
    取得資料表摘要資訊
    """
    from sqlalchemy import inspect
    inspector = inspect(engine)
    summary = []
    for table_name in get_table_names():
        count = 0
        try:
            with engine.connect() as conn:
                result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = result.scalar()
        except:
            pass
        summary.append({
            "table_name": table_name,
            "row_count": count
        })
    return summary
