from typing import Dict, List, Optional
from .database import DBAdapter

class BaseRepository:
    def __init__(self, adapter: DBAdapter):
        self.adapter = adapter
