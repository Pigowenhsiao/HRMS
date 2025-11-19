from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Sequence

class DBAdapter(ABC):
    @abstractmethod
    def list(self, table: str, filters: Optional[Dict[str, str]] = None, limit: Optional[int] = None) -> List[Dict]:
        ...

    @abstractmethod
    def get_by_pk(self, table: str, pk: str, value: str) -> Optional[Dict]:
        ...

    @abstractmethod
    def upsert(self, table: str, pk: str, row: Dict) -> Dict:
        ...

    @abstractmethod
    def delete(self, table: str, pk: str, value: str) -> bool:
        ...

    @abstractmethod
    def list_distinct(self, table: str, column: str) -> List[str]:
        ...
