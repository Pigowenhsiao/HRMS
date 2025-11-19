from __future__ import annotations
from dataclasses import dataclass
from ..config import settings
from .adapters.csv_adapter import CSVAdapter

@dataclass
class UnitOfWork:
    adapter: CSVAdapter

    @classmethod
    def from_settings(cls):
        assert settings.database.backend == "csv", "此骨架以 CSV 為後端"
        return cls(adapter=CSVAdapter(settings.database.csv.data_dir))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # CSV 為檔案儲存，無需額外清理/關閉
        return False
