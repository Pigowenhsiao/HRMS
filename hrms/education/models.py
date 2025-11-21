"""
教育經歷模型
"""
from pydantic import BaseModel, Field
from typing import Optional

class EducationBase(BaseModel):
    Education_ID: Optional[int] = Field(None, description="教育經歷ID")
    EMP_ID: str = Field(..., min_length=1, max_length=10, description="員工編號")
    School_Name: Optional[str] = Field(None, max_length=100, description="學校名稱")
    Major: Optional[str] = Field(None, max_length=100, description="科系")
    Degree: Optional[str] = Field(None, max_length=20, description="學歷")
    Start_Date: Optional[str] = Field(None, description="就學開始日期")
    End_Date: Optional[str] = Field(None, description="就學結束日期")
    GPA: Optional[float] = Field(None, ge=0.0, le=4.0, description="平均成績")

class EducationCreate(EducationBase):
    EMP_ID: str = Field(..., min_length=1, max_length=10, description="員工編號")
    School_Name: str = Field(..., max_length=100, description="學校名稱")

class EducationUpdate(EducationBase):
    pass