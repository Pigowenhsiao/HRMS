from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from .base import Base

class Basic(Base):
    __tablename__ = "BASIC"
    EMP_ID: Mapped[str] = mapped_column(String, primary_key=True)
    Dept_Code: Mapped[str] = mapped_column(String, nullable=True)
    C_Name: Mapped[str] = mapped_column(String, nullable=True)
    On_Board_Date: Mapped[str] = mapped_column(String, nullable=True)  # TODO: Date
    Area: Mapped[str] = mapped_column(String, nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
