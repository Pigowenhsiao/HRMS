"""
Repository 基礎類別
實作通用的 CRUD 操作
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy import inspect

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Repository 基礎類別
    提供通用的資料庫操作方法
    """
    def __init__(self, session: Session, model_class: type):
        self.session = session
        self.model_class = model_class
        self.table_name = model_class.__tablename__
    
    def list(self, filters: Optional[Dict[str, Any]] = None, 
             limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        查詢資料列表
        
        Args:
            filters: 篩選條件
            limit: 回傳筆數限制
            offset: 起始位置（用於分頁）
        
        Returns:
            資料列表
        """
        query = self.session.query(self.model_class)
        
        if filters:
            for column, value in filters.items():
                if hasattr(self.model_class, column) and value is not None:
                    query = query.filter(getattr(self.model_class, column) == value)
        
        query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_by_pk(self, pk: Any) -> Optional[T]:
        """
        依主鍵查詢單筆資料
        
        Args:
            pk: 主鍵值
        
        Returns:
            資料物件或 None
        """
        return self.session.query(self.model_class).get(pk)
    
    def get(self, **kwargs) -> Optional[T]:
        """
        依條件查詢單筆資料
        
        Args:
            **kwargs: 查詢條件
        
        Returns:
            資料物件或 None
        """
        query = self.session.query(self.model_class)
        for key, value in kwargs.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.first()
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        計算資料筆數
        
        Args:
            filters: 篩選條件
        
        Returns:
            資料筆數
        """
        query = self.session.query(self.model_class)
        
        if filters:
            for column, value in filters.items():
                if hasattr(self.model_class, column) and value is not None:
                    query = query.filter(getattr(self.model_class, column) == value)
        
        return query.count()
    
    def exists(self, pk: Any) -> bool:
        """
        檢查資料是否存在
        
        Args:
            pk: 主鍵值
        
        Returns:
            True/False
        """
        return self.get_by_pk(pk) is not None
    
    def create(self, obj: T) -> T:
        """
        新增資料
        
        Args:
            obj: 資料物件
        
        Returns:
            新增的資料物件
        """
        self.session.add(obj)
        self.session.flush()
        return obj
    
    def update(self, pk: Any, data: Dict[str, Any]) -> Optional[T]:
        """
        更新資料
        
        Args:
            pk: 主鍵值
            data: 更新欄位與值
        
        Returns:
            更新後的資料物件或 None
        """
        obj = self.get_by_pk(pk)
        if not obj:
            return None
        
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        self.session.flush()
        return obj
    
    def upsert(self, pk: Any, data: Dict[str, Any]) -> T:
        """
        新增或更新資料（Upsert）
        
        Args:
            pk: 主鍵值
            data: 資料欄位與值
        
        Returns:
            資料物件
        """
        obj = self.get_by_pk(pk)
        if obj:
            # 更新
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            return obj
        else:
            # 新增
            new_obj = self.model_class(**data)
            self.session.add(new_obj)
            self.session.flush()
            return new_obj
    
    def delete(self, pk: Any) -> bool:
        """
        刪除資料
        
        Args:
            pk: 主鍵值
        
        Returns:
            是否成功刪除
        """
        obj = self.get_by_pk(pk)
        if obj:
            self.session.delete(obj)
            self.session.flush()  # 立即執行刪除
            return True
        return False
    
    def list_distinct(self, column: str) -> List[Any]:
        """
        查詢某欄位的不重複值
        
        Args:
            column: 欄位名稱
        
        Returns:
            不重複值列表
        """
        if not hasattr(self.model_class, column):
            return []
        
        query = self.session.query(getattr(self.model_class, column)).distinct()
        results = query.all()
        return [row[0] for row in results if row[0] is not None]


class BaseRepositorySQLAlchemy(BaseRepository[T]):
    """
    SQLAlchemy 實作的 Repository 基礎類別
    """
    
    def __init__(self, session: Session):
        super().__init__(session, self.model_class)


class RepositoryError(Exception):
    """Repository 操作錯誤"""
    pass
