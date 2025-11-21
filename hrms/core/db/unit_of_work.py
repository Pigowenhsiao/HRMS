from __future__ import annotations
from dataclasses import dataclass
from ..config import settings
from .adapters.csv_adapter import CSVAdapter
from .adapters.access_adapter import AccessAdapter

@dataclass
class UnitOfWork:
    adapter: any  # 可以是 CSVAdapter 或 AccessAdapter

    @classmethod
    def from_settings(cls):
        if settings.database.backend == "access":
            return cls(adapter=AccessAdapter(settings.access_db_path))
        else:  # 默認為 CSV
            from pathlib import Path
            # 使用與原始 README 說明一致的配置
            data_dir = Path(settings.database.csv.data_dir)
            return cls(adapter=CSVAdapter(str(data_dir)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # 目前 CSV 和 Access 都無需額外清理/關閉
        # 在未來如果需要特殊處理，可以根據 adapter 類型進行操作
        return False
