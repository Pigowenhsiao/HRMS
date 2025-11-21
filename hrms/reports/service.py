"""
報表集中化系統
"""
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from ..core.db.unit_of_work import UnitOfWork
from ..core.utils.date_utils import parse_date
from ..core.reporting.reports import df_to_excel


class ReportService:
    """報表服務類"""
    
    @staticmethod
    def generate_employee_summary_report(
        only_active: bool = True,
        include_personal_info: bool = False
    ) -> str:
        """
        生成員工摘要報表
        
        Args:
            only_active: 是否只包含在職員工
            include_personal_info: 是否包含個人訊息
            
        Returns:
            Excel 文件路徑
        """
        with UnitOfWork.from_settings() as uow:
            # 獲取員工數據
            employees = uow.adapter.list("Employees", 
                                       filters={"Active": "true"} if only_active else None)
            
            # 如果需要個人訊息，則合併數據
            if include_personal_info:
                personal_info_list = uow.adapter.list("PersonalInfo")
                # 將個人訊息合併到員工數據中
                emp_dict = {emp["EMP_ID"]: emp for emp in employees}
                
                for pInfo in personal_info_list:
                    emp_id = pInfo.get("EMP_ID")
                    if emp_id in emp_dict:
                        # 合併個人訊息到員工記錄
                        emp_dict[emp_id].update({
                            f"Personal_{k}": v for k, v in pInfo.items() 
                            if k != "EMP_ID"  # 避免重複 EMP_ID
                        })
                
                employees = list(emp_dict.values())
        
        # 轉換為 DataFrame 並生成 Excel 報表
        df = pd.DataFrame(employees)
        return df_to_excel(df, prefix="employee_summary")
    
    @staticmethod
    def generate_department_headcount_report() -> str:
        """
        生成部門人數統計報表
        
        Returns:
            Excel 文件路徑
        """
        with UnitOfWork.from_settings() as uow:
            # 獲取在職員工數據
            employees = uow.adapter.list("Employees", filters={"Active": "true"})
            
            # 獲取部門信息
            departments = uow.adapter.list("Departments")
            dept_dict = {dept["Dept_Code"]: dept.get("Dept_Name", dept["Dept_Code"]) 
                         for dept in departments}
        
        # 計算各部門人數
        dept_counts = {}
        for emp in employees:
            dept_code = emp.get("Dept_Code", "Unknown")
            dept_name = dept_dict.get(dept_code, dept_code)
            dept_counts[dept_name] = dept_counts.get(dept_name, 0) + 1
        
        # 創建報表數據
        report_data = []
        for dept_name, count in dept_counts.items():
            report_data.append({
                "Dept_Name": dept_name,
                "Headcount": count
            })
        
        df = pd.DataFrame(report_data)
        return df_to_excel(df, prefix="dept_headcount")
    
    @staticmethod
    def generate_employees_by_area_report() -> str:
        """
        生成按區域分類的員工報表
        
        Returns:
            Excel 文件路徑
        """
        with UnitOfWork.from_settings() as uow:
            # 獲取在職員工數據
            employees = uow.adapter.list("Employees", filters={"Active": "true"})
            
            # 獲取區域信息
            areas = uow.adapter.list("Areas")
            area_dict = {area["Area"]: area.get("Area_Desc", area["Area"]) 
                         for area in areas}
        
        # 按區域分組員工
        area_employees = {}
        for emp in employees:
            area_code = emp.get("Area", "Unknown")
            area_name = area_dict.get(area_code, area_code)
            
            if area_name not in area_employees:
                area_employees[area_name] = []
            area_employees[area_name].append(emp)
        
        # 創建報表數據
        report_data = []
        for area_name, emps in area_employees.items():
            for emp in emps:
                report_data.append({
                    "Area": area_name,
                    "EMP_ID": emp.get("EMP_ID"),
                    "C_Name": emp.get("C_Name"),
                    "Title": emp.get("Title"),
                    "Dept_Code": emp.get("Dept_Code")
                })
        
        df = pd.DataFrame(report_data)
        return df_to_excel(df, prefix="employees_by_area")
    
    @staticmethod
    def generate_service_length_report() -> str:
        """
        生成年資分析報表
        
        Returns:
            Excel 文件路徑
        """
        from ..core.utils.date_utils import calculate_date_difference
        
        with UnitOfWork.from_settings() as uow:
            # 獲取在職員工數據
            employees = uow.adapter.list("Employees", filters={"Active": "true"})
        
        report_data = []
        for emp in employees:
            emp_id = emp.get("EMP_ID")
            name = emp.get("C_Name")
            onboard_date = emp.get("On_Board_Date")
            
            if onboard_date:
                service_days = calculate_date_difference(onboard_date, datetime.now().strftime("%Y-%m-%d"))
                service_years = round(service_days / 365.25, 1) if service_days else 0
            else:
                service_years = 0
                service_days = 0
            
            report_data.append({
                "EMP_ID": emp_id,
                "C_Name": name,
                "On_Board_Date": onboard_date,
                "Service_Years": service_years,
                "Service_Days": service_days
            })
        
        df = pd.DataFrame(report_data)
        return df_to_excel(df, prefix="service_length_analysis")
    
    @staticmethod
    def generate_custom_report(
        table_name: str, 
        filters: Optional[Dict] = None, 
        columns: Optional[List[str]] = None
    ) -> str:
        """
        生成自定義報表
        
        Args:
            table_name: 表格名稱
            filters: 過濾條件
            columns: 要包含的列
            
        Returns:
            Excel 文件路徑
        """
        with UnitOfWork.from_settings() as uow:
            data = uow.adapter.list(table_name, filters=filters)
        
        df = pd.DataFrame(data)
        
        # 如果指定了列，則只選擇這些列
        if columns:
            df = df[[col for col in columns if col in df.columns]]
        
        return df_to_excel(df, prefix=f"custom_{table_name}")


# 簡化的報表生成函數，便於在其他地方使用
def generate_employee_summary(only_active: bool = True) -> str:
    """生成員工摘要報表的簡化函數"""
    return ReportService.generate_employee_summary_report(only_active=only_active)


def generate_department_headcount() -> str:
    """生成部門人數統計報表的簡化函數"""
    return ReportService.generate_department_headcount_report()


def generate_service_length() -> str:
    """生成年資分析報表的簡化函數"""
    return ReportService.generate_service_length_report()