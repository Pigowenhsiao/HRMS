from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class EmployeeBase(BaseModel):
    EMP_ID: str = Field(..., min_length=1, max_length=10, description="員工編號")
    Dept_Code: Optional[str] = Field(None, max_length=10, description="部門代碼")
    C_Name: Optional[str] = Field(None, max_length=50, description="中文姓名")
    Title: Optional[str] = Field(None, max_length=50, description="職稱")
    On_Board_Date: Optional[str] = Field(None, description="到職日期")
    Shift: Optional[str] = Field(None, max_length=10, description="班別")
    Area: Optional[str] = Field(None, max_length=10, description="區域")
    Function: Optional[str] = Field(None, max_length=20, description="職務")
    Meno: Optional[str] = Field(None, max_length=255, description="備註")
    Active: Optional[bool] = Field(True, description="是否在職")
    VAC_ID: Optional[str] = Field(None, max_length=10, description="假別代碼")
    VAC_DESC: Optional[str] = Field(None, max_length=100, description="假別說明")
    Start_date: Optional[str] = Field(None, description="開始日期")
    End_date: Optional[str] = Field(None, description="結束日期")
    AreaDate: Optional[str] = Field(None, description="區域日期")

    @field_validator('EMP_ID')
    @classmethod
    def validate_emp_id(cls, v):
        if not v or len(v) == 0:
            raise ValueError('員工編號不能為空')
        # 驗證員工編號格式（例如：6位數字）
        if not v.isdigit() or len(v) < 4 or len(v) > 10:
            raise ValueError('員工編號必須是4到10位的數字')
        return v

    @field_validator('Active')
    @classmethod
    def validate_active(cls, v):
        if v is None:
            return True
        return bool(v)

class EmployeeCreate(EmployeeBase):
    EMP_ID: str = Field(..., min_length=1, max_length=10, description="員工編號")

class EmployeeUpdate(EmployeeBase):
    EMP_ID: Optional[str] = Field(None, min_length=1, max_length=10, description="員工編號")

class DepartmentBase(BaseModel):
    Dept_Code: str = Field(..., min_length=1, max_length=10, description="部門代碼")
    Dept_Name: Optional[str] = Field(None, max_length=50, description="部門名稱")
    Dept_Desc: Optional[str] = Field(None, max_length=255, description="部門描述")
    Supervisor: Optional[str] = Field(None, max_length=50, description="主管姓名")

    @field_validator('Dept_Code')
    @classmethod
    def validate_dept_code(cls, v):
        if not v or len(v) == 0:
            raise ValueError('部門代碼不能為空')
        return v

class DepartmentCreate(DepartmentBase):
    Dept_Code: str = Field(..., min_length=1, max_length=10, description="部門代碼")

class DepartmentUpdate(DepartmentBase):
    Dept_Code: Optional[str] = Field(None, min_length=1, max_length=10, description="部門代碼")

class AreaBase(BaseModel):
    Area: str = Field(..., min_length=1, max_length=10, description="區域代碼")
    Area_Desc: Optional[str] = Field(None, max_length=100, description="區域說明")
    Active: Optional[bool] = Field(True, description="是否啟用")

    @field_validator('Area')
    @classmethod
    def validate_area(cls, v):
        if not v or len(v) == 0:
            raise ValueError('區域代碼不能為空')
        return v

    @field_validator('Active')
    @classmethod
    def validate_active(cls, v):
        if v is None:
            return True
        return bool(v)

class AreaCreate(AreaBase):
    Area: str = Field(..., min_length=1, max_length=10, description="區域代碼")

class AreaUpdate(AreaBase):
    Area: Optional[str] = Field(None, min_length=1, max_length=10, description="區域代碼")

class JobTypeBase(BaseModel):
    Job_Code: str = Field(..., min_length=1, max_length=10, description="職務代碼")
    Job_Desc: Optional[str] = Field(None, max_length=100, description="職務說明")

    @field_validator('Job_Code')
    @classmethod
    def validate_job_code(cls, v):
        if not v or len(v) == 0:
            raise ValueError('職務代碼不能為空')
        return v

class JobTypeCreate(JobTypeBase):
    Job_Code: str = Field(..., min_length=1, max_length=10, description="職務代碼")

class JobTypeUpdate(JobTypeBase):
    Job_Code: Optional[str] = Field(None, min_length=1, max_length=10, description="職務代碼")

class VacationTypeBase(BaseModel):
    VAC_ID: str = Field(..., min_length=1, max_length=10, description="假別代碼")
    VAC_DESC: Optional[str] = Field(None, max_length=100, description="假別說明")
    Active: Optional[bool] = Field(True, description="是否啟用")

    @field_validator('VAC_ID')
    @classmethod
    def validate_vac_id(cls, v):
        if not v or len(v) == 0:
            raise ValueError('假別代碼不能為空')
        return v

    @field_validator('Active')
    @classmethod
    def validate_active(cls, v):
        if v is None:
            return True
        return bool(v)

class VacationTypeCreate(VacationTypeBase):
    VAC_ID: str = Field(..., min_length=1, max_length=10, description="假別代碼")

class VacationTypeUpdate(VacationTypeBase):
    VAC_ID: Optional[str] = Field(None, min_length=1, max_length=10, description="假別代碼")

class AuthorityBase(BaseModel):
    Account: str = Field(..., min_length=1, max_length=50, description="帳號")
    Auth_Type: Optional[str] = Field(None, max_length=10, description="權限類型")
    Active: Optional[bool] = Field(True, description="是否啟用")

    @field_validator('Account')
    @classmethod
    def validate_account(cls, v):
        if not v or len(v) == 0:
            raise ValueError('帳號不能為空')
        return v

    @field_validator('Active')
    @classmethod
    def validate_active(cls, v):
        if v is None:
            return True
        return bool(v)

class AuthorityCreate(AuthorityBase):
    Account: str = Field(..., min_length=1, max_length=50, description="帳號")

class AuthorityUpdate(AuthorityBase):
    Account: Optional[str] = Field(None, min_length=1, max_length=50, description="帳號")

class PersonalInfoBase(BaseModel):
    EMP_ID: str = Field(..., min_length=1, max_length=10, description="員工編號")
    Birth_Date: Optional[str] = Field(None, description="生日")
    Gender: Optional[str] = Field(None, max_length=10, description="性別")
    ID_Number: Optional[str] = Field(None, max_length=20, description="身分證字號")
    Address: Optional[str] = Field(None, max_length=255, description="地址")
    Phone: Optional[str] = Field(None, max_length=20, description="電話")

    @field_validator('EMP_ID')
    @classmethod
    def validate_emp_id(cls, v):
        if not v or len(v) == 0:
            raise ValueError('員工編號不能為空')
        return v

    @field_validator('ID_Number')
    @classmethod
    def validate_id_number(cls, v):
        if v is not None and len(v) > 0:
            # 驗證台灣身分證字號格式 (1個大寫字母+9個數字)
            if len(v) != 10 or not v[0].isupper() or not v[1:].isdigit():
                raise ValueError('身分證字號格式不正確')
        return v

class PersonalInfoCreate(PersonalInfoBase):
    EMP_ID: str = Field(..., min_length=1, max_length=10, description="員工編號")

class PersonalInfoUpdate(PersonalInfoBase):
    EMP_ID: Optional[str] = Field(None, min_length=1, max_length=10, description="員工編號")