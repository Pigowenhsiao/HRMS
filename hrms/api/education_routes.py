"""
教育經歷 API 端點
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..education.service import (
    list_education_records, 
    get_education_record, 
    create_education_record, 
    update_education_record,
    delete_education_record
)
from ..education.models import EducationCreate, EducationUpdate

router = APIRouter(prefix="/education", tags=["education"])

@router.get("/", response_model=List[dict])
def get_education_list(emp_id: str = None, limit: int = 100):
    """獲取教育經歷列表"""
    try:
        return list_education_records(emp_id=emp_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{edu_id}", response_model=dict)
def get_education_by_id(edu_id: int):
    """獲取特定教育經歷"""
    try:
        result = get_education_record(edu_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
def create_education(education: EducationCreate):
    """創建教育經歷"""
    try:
        data = education.model_dump()
        return create_education_record(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{edu_id}", response_model=dict)
def update_education(edu_id: int, education: EducationUpdate):
    """更新教育經歷"""
    try:
        data = education.model_dump(exclude_unset=True)
        return update_education_record(edu_id, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{edu_id}")
def remove_education(edu_id: int):
    """刪除教育經歷"""
    try:
        result = delete_education_record(edu_id)
        if result:
            return {"message": "教育經歷已成功刪除"}
        else:
            raise HTTPException(status_code=404, detail="教育經歷不存在")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="按ID刪除教育經歷記錄的功能尚未實現")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))