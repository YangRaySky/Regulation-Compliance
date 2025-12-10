"""
儲存層模組

提供資料持久化的抽象介面與實作。
"""

from .interfaces import (
    StorageInterface,
    VectorStoreInterface,
)
from .local import (
    LocalSQLiteStorage,
    LocalChromaVectorStore,
)

__all__ = [
    "StorageInterface",
    "VectorStoreInterface",
    "LocalSQLiteStorage",
    "LocalChromaVectorStore",
]
