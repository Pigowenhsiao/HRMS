"""
報表 API 端點
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
from ..reports.service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/employee-summary")
def get_employee_summary_report(only_active: bool = True, include_personal_info: bool = False):
    """獲取員工摘要報表"""
    try:
        file_path = ReportService.generate_employee_summary_report(
            only_active=only_active,
            include_personal_info=include_personal_info
        )
        return {"report_path": file_path, "message": "報表已生成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/department-headcount")
def get_department_headcount_report():
    """獲取部門人數統計報表"""
    try:
        file_path = ReportService.generate_department_headcount_report()
        return {"report_path": file_path, "message": "報表已生成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employees-by-area")
def get_employees_by_area_report():
    """獲取按區域分類的員工報表"""
    try:
        file_path = ReportService.generate_employees_by_area_report()
        return {"report_path": file_path, "message": "報表已生成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/service-length-analysis")
def get_service_length_report():
    """獲取年資分析報表"""
    try:
        file_path = ReportService.generate_service_length_report()
        return {"report_path": file_path, "message": "報表已生成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/custom")
def get_custom_report(
    table_name: str, 
    filters: Dict = None, 
    columns: list = None
):
    """獲取自定義報表"""
    try:
        file_path = ReportService.generate_custom_report(
            table_name=table_name,
            filters=filters,
            columns=columns
        )
        return {"report_path": file_path, "message": "報表已生成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))