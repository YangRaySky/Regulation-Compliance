"""
爬蟲基礎類別

定義爬蟲的抽象介面與共用功能。
"""

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import httpx


@dataclass
class CrawlerResult:
    """
    爬蟲結果資料類別
    """
    status: str  # success, partial, failed
    source_name: str
    source_url: str
    content: str
    content_type: str  # html, pdf, text, json
    retrieved_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def content_hash(self) -> str:
        """計算內容雜湊值"""
        return hashlib.sha256(self.content.encode()).hexdigest()

    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "status": self.status,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "content": self.content,
            "content_type": self.content_type,
            "retrieved_at": self.retrieved_at.isoformat(),
            "metadata": self.metadata,
            "error": self.error,
            "content_hash": self.content_hash,
        }


class BaseCrawler(ABC):
    """
    爬蟲基礎抽象類別

    所有法規爬蟲都應繼承此類別。
    """

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        """
        初始化爬蟲

        Args:
            timeout: 請求超時時間 (秒)
            max_retries: 最大重試次數
            retry_delay: 重試間隔 (秒)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[httpx.AsyncClient] = None

    @property
    @abstractmethod
    def source_name(self) -> str:
        """資料來源名稱"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """基礎 URL"""
        pass

    async def get_client(self) -> httpx.AsyncClient:
        """取得 HTTP 客戶端"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "RegulationComplianceAgent/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
                },
            )
        return self._client

    async def close(self):
        """關閉 HTTP 客戶端"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def fetch_url(
        self,
        url: str,
        method: str = "GET",
        **kwargs,
    ) -> tuple[str, int]:
        """
        擷取 URL 內容

        Args:
            url: 目標 URL
            method: HTTP 方法
            **kwargs: 傳遞給 httpx 的額外參數

        Returns:
            (內容, 狀態碼)
        """
        import asyncio

        client = await self.get_client()
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = await client.request(method, url, **kwargs)
                return response.text, response.status_code

            except httpx.HTTPError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        raise last_error or Exception("未知錯誤")

    @abstractmethod
    async def search(
        self,
        query: str,
        **kwargs,
    ) -> list[dict]:
        """
        搜尋法規

        Args:
            query: 搜尋關鍵字
            **kwargs: 額外參數

        Returns:
            搜尋結果列表
        """
        pass

    @abstractmethod
    async def get_regulation(
        self,
        regulation_id: str,
    ) -> CrawlerResult:
        """
        取得單一法規內容

        Args:
            regulation_id: 法規識別碼

        Returns:
            爬蟲結果
        """
        pass

    async def __aenter__(self):
        """Context manager 進入"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager 離開"""
        await self.close()
