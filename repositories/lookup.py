"""
對照表 Repository
包含部門、區域、職務、假別、班別、工站
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from domain.models import Section, Area, Job, VacType, Shift, Shop
from .base import BaseRepositorySQLAlchemy

class SectionRepository(BaseRepositorySQLAlchemy[Section]):
    """部門 Repository"""
    model_class = Section
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_active_sections(self) -> List[Section]:
        """取得有效的部門"""
        return self.session.query(Section).all()

class AreaRepository(BaseRepositorySQLAlchemy[Area]):
    """區域 Repository"""
    model_class = Area
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_active_areas(self) -> List[Area]:
        """取得有效的區域"""
        return self.list(filters={"Active": True})

class JobRepository(BaseRepositorySQLAlchemy[Job]):
    """職務 Repository"""
    model_class = Job
    
    def __init__(self, session: Session):
        super().__init__(session)

class VacTypeRepository(BaseRepositorySQLAlchemy[VacType]):
    """假別 Repository"""
    model_class = VacType
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_active_vac_types(self) -> List[VacType]:
        """取得有效的假別"""
        return self.list(filters={"Active": True})

class ShiftRepository(BaseRepositorySQLAlchemy[Shift]):
    """班別 Repository"""
    model_class = Shift
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_by_section(self, dept_code: str) -> List[Shift]:
        """依部門查詢班別"""
        return self.list(filters={"L_Section": dept_code})
    
    def get_active_shifts(self) -> List[Shift]:
        """取得有效的班別"""
        return self.list(filters={"Active": True})

class ShopRepository(BaseRepositorySQLAlchemy[Shop]):
    """工站 Repository"""
    model_class = Shop
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_active_shops(self) -> List[Shop]:
        """取得有效的工站"""
        return self.list(filters={"Active": True})

class LookupService:
    """
    對照表服務
    提供下拉選單資料，並支援快取
    """
    
    def __init__(self, session: Session):
        self.session = session
        self._cache = {}
        
        # 初始化 Repository
        self.section_repo = SectionRepository(session)
        self.area_repo = AreaRepository(session)
        self.job_repo = JobRepository(session)
        self.vac_type_repo = VacTypeRepository(session)
        self.shift_repo = ShiftRepository(session)
        self.shop_repo = ShopRepository(session)
    
    # === 部門相關 ===
    def list_dept_codes(self) -> List[str]:
        """取得所有部門代碼"""
        cache_key = "dept_codes"
        if cache_key not in self._cache:
            sections = self.section_repo.get_active_sections()
            self._cache[cache_key] = [s.Dept_Code for s in sections if s.Dept_Code]
        return self._cache[cache_key]
    
    def list_dept_names(self) -> List[str]:
        """取得所有部門名稱"""
        cache_key = "dept_names"
        if cache_key not in self._cache:
            sections = self.section_repo.get_active_sections()
            self._cache[cache_key] = [s.Dept_Name for s in sections if s.Dept_Name]
        return self._cache[cache_key]
    
    def get_dept_name(self, dept_code: str) -> Optional[str]:
        """依部門代碼取得部門名稱"""
        section = self.section_repo.get_by_pk(dept_code)
        return section.Dept_Name if section else None
    
    # === 區域相關 ===
    def list_areas(self) -> List[str]:
        """取得所有區域代碼"""
        cache_key = "areas"
        if cache_key not in self._cache:
            areas = self.area_repo.get_active_areas()
            self._cache[cache_key] = [a.Area for a in areas if a.Area]
        return self._cache[cache_key]
    
    def list_area_descriptions(self) -> List[str]:
        """取得所有區域說明"""
        cache_key = "area_descs"
        if cache_key not in self._cache:
            areas = self.area_repo.get_active_areas()
            self._cache[cache_key] = [a.Area_Desc for a in areas if a.Area_Desc]
        return self._cache[cache_key]
    
    # === 職務相關 ===
    def list_jobs(self) -> List[str]:
        """取得所有職務"""
        cache_key = "jobs"
        if cache_key not in self._cache:
            jobs = self.job_repo.list()
            self._cache[cache_key] = [j.L_Job for j in jobs if j.L_Job]
        return self._cache[cache_key]
    
    # === 假別相關 ===
    def list_vac_types(self) -> List[str]:
        """取得所有假別代碼"""
        cache_key = "vac_types"
        if cache_key not in self._cache:
            vac_types = self.vac_type_repo.get_active_vac_types()
            self._cache[cache_key] = [v.VAC_ID for v in vac_types if v.VAC_ID]
        return self._cache[cache_key]
    
    def list_vac_type_descs(self) -> List[str]:
        """取得所有假別說明"""
        cache_key = "vac_descs"
        if cache_key not in self._cache:
            vac_types = self.vac_type_repo.get_active_vac_types()
            self._cache[cache_key] = [v.VAC_DESC for v in vac_types if v.VAC_DESC]
        return self._cache[cache_key]
    
    # === 班別相關 ===
    def list_shifts(self) -> List[str]:
        """取得所有班別代碼"""
        cache_key = "shifts"
        if cache_key not in self._cache:
            shifts = self.shift_repo.get_active_shifts()
            self._cache[cache_key] = [s.Shift for s in shifts if s.Shift]
        return self._cache[cache_key]
    
    def list_shifts_by_section(self, dept_code: str) -> List[str]:
        """依部門取得班別"""
        shifts = self.shift_repo.get_by_section(dept_code)
        return [s.Shift for s in shifts if s.Shift]
    
    # === 工站相關 ===
    def list_shop_codes(self) -> List[str]:
        """取得所有工站代碼"""
        cache_key = "shop_codes"
        if cache_key not in self._cache:
            shops = self.shop_repo.get_active_shops()
            self._cache[cache_key] = [s.SHOP for s in shops if s.SHOP]
        return self._cache[cache_key]
    
    def list_shop_descs(self) -> List[str]:
        """取得所有工站說明"""
        cache_key = "shop_descs"
        if cache_key not in self._cache:
            shops = self.shop_repo.get_active_shops()
            self._cache[cache_key] = [s.SHOP_DESC for s in shops if s.SHOP_DESC]
        return self._cache[cache_key]
    
    def clear_cache(self):
        """清除快取"""
        self._cache.clear()
