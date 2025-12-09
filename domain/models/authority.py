from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, ForeignKey, Text, Integer
from .base import Base

class Authority(Base):
    """
    權限管理 (Authority)
    使用者帳號與權限設定
    """
    __tablename__ = "Authority"
    
    S_Account: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
    Update_Date: Mapped[str] = mapped_column(String(20), nullable=True)
    Auth_type: Mapped[str] = mapped_column(String(10), nullable=True)  # 01=Admin, 02=User, 等等

class DelAuthority(Base):
    """
    刪除權限管理 (DEL_AUTHORITY)
    刪除操作的權限設定
    """
    __tablename__ = "DEL_AUTHORITY"
    
    Account_ID: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    S_Account: Mapped[str] = mapped_column(String(50), ForeignKey("Authority.S_Account"), nullable=True)
    Del_Auth: Mapped[bool] = mapped_column(Boolean, default=False)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
    Update_Date: Mapped[str] = mapped_column(String(20), nullable=True)
