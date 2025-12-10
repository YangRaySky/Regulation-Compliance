"""
儲存層抽象介面

定義儲存操作的抽象介面，支援本機/雲端無縫切換。
"""

from abc import ABC, abstractmethod
from typing import Optional, Any

from ..models.regulation import Regulation, ValidationReport, TranslationResult


class StorageInterface(ABC):
    """
    結構化資料儲存介面

    定義法規資料的 CRUD 操作。
    """

    @abstractmethod
    async def save_regulation(self, regulation: Regulation) -> str:
        """
        儲存法規資料

        Args:
            regulation: 法規資料物件

        Returns:
            法規識別碼
        """
        pass

    @abstractmethod
    async def get_regulation(self, regulation_id: str) -> Optional[Regulation]:
        """
        取得法規資料

        Args:
            regulation_id: 法規識別碼

        Returns:
            法規資料物件，若不存在則回傳 None
        """
        pass

    @abstractmethod
    async def list_regulations(
        self,
        jurisdiction: Optional[str] = None,
        regulation_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Regulation]:
        """
        列出法規資料

        Args:
            jurisdiction: 司法管轄區篩選
            regulation_type: 法規類型篩選
            limit: 回傳筆數上限
            offset: 跳過筆數

        Returns:
            法規資料列表
        """
        pass

    @abstractmethod
    async def update_regulation(self, regulation: Regulation) -> bool:
        """
        更新法規資料

        Args:
            regulation: 更新後的法規資料物件

        Returns:
            是否更新成功
        """
        pass

    @abstractmethod
    async def delete_regulation(self, regulation_id: str) -> bool:
        """
        刪除法規資料

        Args:
            regulation_id: 法規識別碼

        Returns:
            是否刪除成功
        """
        pass

    @abstractmethod
    async def save_validation_report(self, report: ValidationReport) -> str:
        """
        儲存驗證報告

        Args:
            report: 驗證報告物件

        Returns:
            驗證報告識別碼
        """
        pass

    @abstractmethod
    async def get_validation_reports(
        self,
        regulation_id: str,
        limit: int = 10,
    ) -> list[ValidationReport]:
        """
        取得法規的驗證報告歷史

        Args:
            regulation_id: 法規識別碼
            limit: 回傳筆數上限

        Returns:
            驗證報告列表
        """
        pass

    @abstractmethod
    async def save_translation(self, translation: TranslationResult) -> str:
        """
        儲存翻譯結果

        Args:
            translation: 翻譯結果物件

        Returns:
            翻譯識別碼
        """
        pass


class VectorStoreInterface(ABC):
    """
    向量資料庫介面

    定義向量搜尋相關操作。
    """

    @abstractmethod
    async def add_documents(
        self,
        documents: list[dict],
        embeddings: Optional[list[list[float]]] = None,
    ) -> list[str]:
        """
        新增文件到向量資料庫

        Args:
            documents: 文件列表，每個文件包含 content, metadata
            embeddings: 預計算的向量（可選）

        Returns:
            文件 ID 列表
        """
        pass

    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None,
    ) -> list[dict]:
        """
        相似度搜尋

        Args:
            query: 查詢文字
            k: 回傳筆數
            filter: 元資料篩選條件

        Returns:
            相似文件列表，包含 content, metadata, score
        """
        pass

    @abstractmethod
    async def delete_documents(self, document_ids: list[str]) -> bool:
        """
        刪除文件

        Args:
            document_ids: 文件 ID 列表

        Returns:
            是否刪除成功
        """
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[dict]:
        """
        取得單一文件

        Args:
            document_id: 文件 ID

        Returns:
            文件資料，若不存在則回傳 None
        """
        pass

    @abstractmethod
    async def update_document(
        self,
        document_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        更新文件

        Args:
            document_id: 文件 ID
            content: 更新的內容
            metadata: 更新的元資料

        Returns:
            是否更新成功
        """
        pass


class CacheInterface(ABC):
    """
    快取介面

    定義快取操作。
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        取得快取值

        Args:
            key: 快取鍵

        Returns:
            快取值，若不存在則回傳 None
        """
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        設定快取值

        Args:
            key: 快取鍵
            value: 快取值
            ttl: 存活時間（秒）

        Returns:
            是否設定成功
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        刪除快取

        Args:
            key: 快取鍵

        Returns:
            是否刪除成功
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        檢查快取是否存在

        Args:
            key: 快取鍵

        Returns:
            是否存在
        """
        pass
