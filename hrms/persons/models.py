from pydantic import BaseModel, Field
from typing import Optional
from ..core.models import EmployeeBase

# 使用從 core.models 導入的 EmployeeBase 作為基礎模型
# 這保持了與現有架構的兼容性，同時增加了驗證功能
class BasicRow(EmployeeBase):
    pass
