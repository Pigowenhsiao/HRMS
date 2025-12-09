"""
SQLite UnitOfWork
提供 SQLAlchemy Session 管理與交易控制
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from pathlib import Path
import os

# 資料庫設定
def _get_engine():
    """取得資料庫引擎"""
    # 從環境變數取得資料庫路徑
    db_url = os.getenv("DB_URL", "sqlite:///./hrms.db")
    
    # 處理 SQLite 路徑
    if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:////"):
        db_path = Path(db_url.replace("sqlite:///", ""))
        if not db_path.is_absolute():
            db_path = Path(__file__).resolve().parents[3] / db_path
        db_url = f"sqlite:///{db_path}"
    
    return create_engine(db_url, echo=False, future=True)

def _get_session_factory():
    """取得 Session 工廠"""
    engine = _get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# 全域引擎與 Session 工廠
_engine = _get_engine()
_SessionFactory = _get_session_factory()

@dataclass
class UnitOfWork:
    """
    SQLite 資料庫的 UnitOfWork
    提供自動的 Session 管理與交易控制
    
    使用範例：
        with UnitOfWork() as uow:
            repo = BasicRepository(uow.session)
            employee = repo.get_by_pk("000056")
            # 自動 Commit
    
        with UnitOfWork() as uow:
            repo = BasicRepository(uow.session)
            try:
                repo.delete("non_exist")
                # 發生錯誤，自動 Rollback
            except Exception as e:
                pass
    """
    session: Optional[Session] = None
    
    def __enter__(self):
        """進入上下文，建立 Session"""
        if self.session is None:
            self.session = _SessionFactory()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """離開上下文，處理交易"""
        if self.session is None:
            return False
        
        try:
            if exc_type is not None:
                # 發生例外，Rollback
                self.session.rollback()
                return False  # 不抑制例外，讓它傳播
            else:
                # 正常結束，Commit
                self.session.commit()
                return True
        finally:
            # 關閉 Session
            self.session.close()
            self.session = None
    
    @classmethod
    def create(cls) -> 'UnitOfWork':
        """建立 UnitOfWork 實例"""
        return cls()

# 相容性別名
UnitOfWorkSQLite = UnitOfWork
