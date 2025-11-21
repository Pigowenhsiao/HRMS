"""
個人訊息 API 端點
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..personal_info.service import (
    list_personal_info, 
    get_personal_info, 
    upsert_personal_info, 
    delete_personal_info
)
from ..core.models import PersonalInfoCreate, PersonalInfoUpdate

router = APIRouter(prefix="/personal-info", tags=["personal-info"])

@router.get("/", response_model=List[dict])
def get_personal_info_list(only_active: bool = True, limit: int = 100):
    """獲取個人訊息列表"""
    try:
        return list_personal_info(only_active=only_active, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{emp_id}", response_model=dict)
def get_personal_info_by_id(emp_id: str):
    """獲取特定員工的個人訊息"""
    try:
        result = get_personal_info(emp_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
def create_personal_info(personal_info: PersonalInfoCreate):
    """創建個人訊息"""
    try:
        data = personal_info.model_dump()
        return upsert_personal_info(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{emp_id}", response_model=dict)
def update_personal_info(emp_id: str, personal_info: PersonalInfoUpdate):
    """更新個人訊息"""
    try:
        data = personal_info.model_dump(exclude_unset=True)
        data["EMP_ID"] = emp_id
        return upsert_personal_info(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{emp_id}")
def remove_personal_info(emp_id: str):
    """刪除個人訊息"""
    try:
        result = delete_personal_info(emp_id)
        if result:
            return {"message": "個人訊息已成功刪除"}
        else:
            raise HTTPException(status_code=404, detail="個人訊息不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))