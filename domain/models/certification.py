from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, ForeignKey, Text, Integer, Float
from .base import Base

class Certify(Base):
    """
    證照狀態對照表 (CERTIFY)
    證照狀態：NEW, ReCer, MO, Over_Due
    """
    __tablename__ = "CERTIFY"
    
    識別碼: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    Certify: Mapped[str] = mapped_column(String(50), nullable=True)
    Certify_Desc: Mapped[str] = mapped_column(String(200), nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)

class CertifyType(Base):
    """
    證照類型 (CERTIFY_TYPE)
    Main Tool, 附屬機台, 訓練項目, 支援項目
    """
    __tablename__ = "CERTIFY_TYPE"
    
    Certify_Type: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)

class CertifyItem(Base):
    """
    證照項目主檔 (CERTIFY_ITEMS)
    所有可取得的證照項目
    """
    __tablename__ = "CERTIFY_ITEMS"
    
    Dept: Mapped[str] = mapped_column(String(50), ForeignKey("L_Section.Dept_Code"), primary_key=True, nullable=False)
    Certify_ID: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    Certify_Type: Mapped[str] = mapped_column(String(50), ForeignKey("CERTIFY_TYPE.Certify_Type"), nullable=True)
    Certify_Name: Mapped[str] = mapped_column(String(500), nullable=True)
    Certify_time: Mapped[str] = mapped_column(String(20), nullable=True)
    Certify_Grade: Mapped[str] = mapped_column(String(50), nullable=True)
    Remark: Mapped[str] = mapped_column(Text, nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
    Score: Mapped[float] = mapped_column(Float, nullable=True)

class TrainingRecord(Base):
    """
    證照記錄 (TRAINING_RECORD)
    員工取得的證照記錄（主要記錄檔）
    """
    __tablename__ = "TRAINING_RECORD"
    
    Certify_No: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    EMP_ID: Mapped[str] = mapped_column(String(50), ForeignKey("BASIC.EMP_ID"), nullable=False)
    Certify_ID: Mapped[str] = mapped_column(String(50), ForeignKey("CERTIFY_ITEMS.Certify_ID"), nullable=False)
    Certify_date: Mapped[str] = mapped_column(String(20), nullable=True)
    Certify_type: Mapped[str] = mapped_column(String(50), nullable=True)
    update_date: Mapped[str] = mapped_column(String(20), nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
    Remark: Mapped[str] = mapped_column(Text, nullable=True)
    updater: Mapped[str] = mapped_column(String(50), nullable=True)
    Cer_type: Mapped[str] = mapped_column(String(10), nullable=True)

class CertifyRecord(Base):
    """
    證照記錄 2 (CERTIFY_RECORD)
    另一種格式的證照記錄
    """
    __tablename__ = "CERTIFY_RECORD"
    
    識別碼: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    EMP_ID: Mapped[str] = mapped_column(String(50), ForeignKey("BASIC.EMP_ID"), nullable=True)
    Certify_NO: Mapped[str] = mapped_column(String(50), nullable=True)
    Update_date: Mapped[str] = mapped_column(String(20), nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
    Meno: Mapped[str] = mapped_column(Text, nullable=True)
    Type: Mapped[str] = mapped_column(String(50), nullable=True)

class CertifyToolMap(Base):
    """
    證照工具對應 (CERTIFY_TOOL_MAP)
    證照與工具的對應關係
    注意：CSV 中有重複資料，所以不使用複合主鍵
    """
    __tablename__ = "CERTIFY_TOOL_MAP"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Certify_ID: Mapped[str] = mapped_column(String(50), ForeignKey("CERTIFY_ITEMS.Certify_ID"), nullable=False)
    TOOL_ID: Mapped[str] = mapped_column(String(50), nullable=False)
    Update_date: Mapped[str] = mapped_column(String(20), nullable=True)
    Remark: Mapped[str] = mapped_column(Text, nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)

class MustTool(Base):
    """
    必需工具 (MUST_TOOL)
    必需的工具清單
    """
    __tablename__ = "MUST_TOOL"
    
    Tool_ID: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)

class Software(Base):
    """
    軟體版本記錄 (SOFTWARE)
    軟體版本變更記錄
    """
    __tablename__ = "SOFTWARE"
    
    S_Ver: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    Meno: Mapped[str] = mapped_column(Text, nullable=True)
    Update_Date: Mapped[str] = mapped_column(String(20), nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
