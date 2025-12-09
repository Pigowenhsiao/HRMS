from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, Integer
from .base import Base
from typing import List

class Section(Base):
    """部門資料表 (L_Section)"""
    __tablename__ = "L_Section"
    
    Dept_Code: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    Dept_Name: Mapped[str] = mapped_column(String(200), nullable=True)
    Dept_Desc: Mapped[str] = mapped_column(String(200), nullable=True)
    Supervisor: Mapped[str] = mapped_column(String(50), nullable=True)

class Area(Base):
    """區域資料表"""
    __tablename__ = "Area"
    
    Area: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    Area_Desc: Mapped[str] = mapped_column(String(200), nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)

class Job(Base):
    """職務資料表 (L_Job)"""
    __tablename__ = "L_Job"
    
    L_Job: Mapped[str] = mapped_column(String(100), primary_key=True, nullable=False)

class VacType(Base):
    """假別資料表 (VAC_Type)"""
    __tablename__ = "VAC_Type"
    
    VAC_ID: Mapped[str] = mapped_column(String(10), primary_key=True, nullable=False)
    VAC_DESC: Mapped[str] = mapped_column(String(100), nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)

class Shift(Base):
    """班別資料表"""
    __tablename__ = "SHIFT"
    
    識別碼: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    Shift: Mapped[str] = mapped_column(String(50), nullable=True)
    L_Section: Mapped[str] = mapped_column(String(50), ForeignKey("L_Section.Dept_Code"), nullable=True)
    Shift_Desc: Mapped[str] = mapped_column(String(200), nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
    Supervisor: Mapped[str] = mapped_column(String(50), nullable=True)

class Shop(Base):
    """工站資料表"""
    __tablename__ = "SHOP"
    
    SHOP: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    SHOP_DESC: Mapped[str] = mapped_column(String(200), nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
