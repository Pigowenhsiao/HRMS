"""
Repository 層
提供資料存取與商業邏輯封裝
"""

# Base Repository
from .base import BaseRepository, BaseRepositorySQLAlchemy, RepositoryError

# Employee Repository
from .employee import BasicRepository, PersonInfoRepository

# Lookup Repository
from .lookup import (
    SectionRepository, AreaRepository, JobRepository,
    VacTypeRepository, ShiftRepository, ShopRepository,
    LookupService
)

# Certification Repository
from .certification import (
    CertifyRepository, CertifyTypeRepository,
    CertifyItemRepository, TrainingRecordRepository,
    CertifyRecordRepository, CertifyToolMapRepository,
    CertificationService
)

# Authority Repository
from .authority import (
    AuthorityRepository, DelAuthorityRepository,
    AuthorizationService
)

__all__ = [
    # Base
    "BaseRepository",
    "BaseRepositorySQLAlchemy",
    "RepositoryError",
    
    # Employee
    "BasicRepository",
    "PersonInfoRepository",
    
    # Lookup
    "SectionRepository",
    "AreaRepository",
    "JobRepository",
    "VacTypeRepository",
    "ShiftRepository",
    "ShopRepository",
    "LookupService",
    
    # Certification
    "CertifyRepository",
    "CertifyTypeRepository",
    "CertifyItemRepository",
    "TrainingRecordRepository",
    "CertifyRecordRepository",
    "CertifyToolMapRepository",
    "CertificationService",
    
    # Authority
    "AuthorityRepository",
    "DelAuthorityRepository",
    "AuthorizationService",
]
