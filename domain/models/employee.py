from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, ForeignKey, Text, Integer
from .base import Base

class Basic(Base):
    """
    員工基本資料表 (BASIC)
    主要員工主檔，包含基本人事資訊
    """
    __tablename__ = "BASIC"
    
    # 主鍵
    EMP_ID: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    
    # 基本資訊
    Dept_Code: Mapped[str] = mapped_column(String(50), ForeignKey("L_Section.Dept_Code"), nullable=True)
    C_Name: Mapped[str] = mapped_column(String(100), nullable=True)
    Title: Mapped[str] = mapped_column(String(100), nullable=True)
    On_Board_Date: Mapped[str] = mapped_column(String(20), nullable=True)
    
    # 班別與工站
    SHIFT: Mapped[str] = mapped_column(String(50), ForeignKey("SHIFT.Shift"), nullable=True)
    Shop: Mapped[str] = mapped_column(String(50), ForeignKey("SHOP.SHOP"), nullable=True)
    
    # 備註與更新
    Meno: Mapped[str] = mapped_column(Text, nullable=True)
    Update_Date: Mapped[str] = mapped_column(String(20), nullable=True)
    
    # 狀態
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 職務與區域
    Function: Mapped[str] = mapped_column(String(50), ForeignKey("L_Job.L_Job"), nullable=True)
    Area: Mapped[str] = mapped_column(String(50), ForeignKey("Area.Area"), nullable=True)
    
    # 調動資訊
    Trans_out_date: Mapped[str] = mapped_column(String(20), nullable=True)
    Area_date: Mapped[str] = mapped_column(String(20), nullable=True)
    Certify_Area: Mapped[str] = mapped_column(String(50), ForeignKey("Area.Area"), nullable=True)
    
    # 假期資訊
    Start_Date: Mapped[str] = mapped_column(String(20), nullable=True)
    End_Date: Mapped[str] = mapped_column(String(20), nullable=True)
    Vac_type: Mapped[str] = mapped_column(String(20), nullable=True)
    VAC_ID: Mapped[str] = mapped_column(String(10), ForeignKey("VAC_Type.VAC_ID"), nullable=True)
    
    # 工作階段
    Work_Stage: Mapped[str] = mapped_column(String(50), nullable=True)

class PersonInfo(Base):
    """
    員工個人資訊表 (PERSON_INFO)
    員工個人詳細資訊，與 BASIC 一對一關聯
    """
    __tablename__ = "PERSON_INFO"
    
    EMP_ID: Mapped[str] = mapped_column(String(50), ForeignKey("BASIC.EMP_ID"), primary_key=True, nullable=False)
    
    # 個人資訊
    Sex: Mapped[str] = mapped_column(String(10), nullable=True)
    Birthday: Mapped[str] = mapped_column(String(20), nullable=True)
    Personal_ID: Mapped[str] = mapped_column(String(50), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    
    # 聯絡方式
    Home_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    Current_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    Cell_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    Person_Phone: Mapped[str] = mapped_column(String(50), nullable=True)
    CUR_PHONE: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # 緊急聯絡人 1
    EMG_NAME1: Mapped[str] = mapped_column(String(100), nullable=True)
    EMG_Phone1: Mapped[str] = mapped_column(String(50), nullable=True)
    EMG_Releasion1: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # 緊急聯絡人 2
    EMG_NAME2: Mapped[str] = mapped_column(String(100), nullable=True)
    EMG_Phone2: Mapped[str] = mapped_column(String(50), nullable=True)
    EMG_Releasion2: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # 居住地
    Living_place: Mapped[str] = mapped_column(String(200), nullable=True)
    Living_Place2: Mapped[str] = mapped_column(String(200), nullable=True)
    
    # 經歷
    Perf_year: Mapped[str] = mapped_column(String(20), nullable=True)
    excomp_year: Mapped[str] = mapped_column(String(20), nullable=True)
    ex_compy_type: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # 異動資訊
    Update_Date: Mapped[str] = mapped_column(String(20), nullable=True)
    Updater_Date: Mapped[str] = mapped_column(String(20), nullable=True)
    Updater: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # 備註
    Meno: Mapped[str] = mapped_column(Text, nullable=True)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
