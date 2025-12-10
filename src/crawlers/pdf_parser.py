"""
PDF 解析器模組

支援從 PDF 文件中提取法規文本，包含：
- 純文字提取 (pdfplumber)
- 表格提取
- 掃描文件 OCR (可選)
- 結構化內容分析
"""

import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx
import pdfplumber
from pdfplumber.page import Page

from .base import CrawlerResult


@dataclass
class PDFPage:
    """PDF 單頁內容"""
    page_number: int
    text: str
    tables: list[list[list[str]]] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class PDFDocument:
    """PDF 文件結構"""
    filename: str
    total_pages: int
    pages: list[PDFPage]
    metadata: dict = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        """取得完整文字內容"""
        return "\n\n".join(
            f"[第 {p.page_number} 頁]\n{p.text}"
            for p in self.pages
        )

    @property
    def all_tables(self) -> list[dict]:
        """取得所有表格"""
        tables = []
        for page in self.pages:
            for i, table in enumerate(page.tables):
                tables.append({
                    "page": page.page_number,
                    "table_index": i,
                    "data": table,
                })
        return tables


class PDFParser:
    """
    PDF 解析器

    使用 pdfplumber 提取 PDF 內容，支援：
    - 本地檔案
    - URL 下載
    - 二進位資料流
    """

    def __init__(
        self,
        timeout: int = 60,
        max_pages: Optional[int] = None,
        extract_tables: bool = True,
    ):
        """
        初始化 PDF 解析器

        Args:
            timeout: 下載超時時間 (秒)
            max_pages: 最大解析頁數 (None 表示全部)
            extract_tables: 是否提取表格
        """
        self.timeout = timeout
        self.max_pages = max_pages
        self.extract_tables = extract_tables

    async def download_pdf(self, url: str) -> bytes:
        """
        從 URL 下載 PDF 檔案

        Args:
            url: PDF 檔案 URL

        Returns:
            PDF 二進位內容
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={
                    "User-Agent": "RegulationComplianceAgent/1.0",
                    "Accept": "application/pdf,*/*",
                },
            )
            response.raise_for_status()

            # 驗證是否為 PDF
            content_type = response.headers.get("content-type", "")
            if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
                # 嘗試檢查檔案魔術數字
                if not response.content.startswith(b"%PDF"):
                    raise ValueError(f"下載的檔案不是 PDF 格式: {content_type}")

            return response.content

    def parse_from_bytes(
        self,
        pdf_bytes: bytes,
        filename: str = "document.pdf",
    ) -> PDFDocument:
        """
        從二進位資料解析 PDF

        Args:
            pdf_bytes: PDF 二進位內容
            filename: 檔案名稱

        Returns:
            PDFDocument 結構
        """
        pages = []

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            metadata = pdf.metadata or {}
            total_pages = len(pdf.pages)

            # 決定要解析的頁數
            pages_to_parse = pdf.pages
            if self.max_pages:
                pages_to_parse = pdf.pages[:self.max_pages]

            for page in pages_to_parse:
                page_content = self._extract_page_content(page)
                pages.append(page_content)

        return PDFDocument(
            filename=filename,
            total_pages=total_pages,
            pages=pages,
            metadata=metadata,
        )

    def parse_from_file(self, filepath: str | Path) -> PDFDocument:
        """
        從本地檔案解析 PDF

        Args:
            filepath: PDF 檔案路徑

        Returns:
            PDFDocument 結構
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"檔案不存在: {filepath}")

        with open(filepath, "rb") as f:
            pdf_bytes = f.read()

        return self.parse_from_bytes(pdf_bytes, filename=filepath.name)

    async def parse_from_url(self, url: str) -> PDFDocument:
        """
        從 URL 下載並解析 PDF

        Args:
            url: PDF 檔案 URL

        Returns:
            PDFDocument 結構
        """
        # 從 URL 提取檔名
        parsed = urlparse(url)
        filename = Path(parsed.path).name or "document.pdf"

        # 下載 PDF
        pdf_bytes = await self.download_pdf(url)

        # 解析 PDF
        return self.parse_from_bytes(pdf_bytes, filename=filename)

    def _extract_page_content(self, page: Page) -> PDFPage:
        """
        提取單頁內容

        Args:
            page: pdfplumber Page 物件

        Returns:
            PDFPage 結構
        """
        # 提取文字
        text = page.extract_text() or ""

        # 清理文字
        text = self._clean_text(text)

        # 提取表格
        tables = []
        if self.extract_tables:
            try:
                raw_tables = page.extract_tables() or []
                tables = [
                    [[cell or "" for cell in row] for row in table]
                    for table in raw_tables
                ]
            except Exception:
                pass

        return PDFPage(
            page_number=page.page_number,
            text=text,
            tables=tables,
            metadata={
                "width": page.width,
                "height": page.height,
            },
        )

    def _clean_text(self, text: str) -> str:
        """
        清理提取的文字

        Args:
            text: 原始文字

        Returns:
            清理後的文字
        """
        # 移除多餘空白
        text = re.sub(r"\s+", " ", text)

        # 移除頁首頁尾常見模式 (可根據需要擴充)
        text = re.sub(r"^\s*第\s*\d+\s*頁\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*第\s*\d+\s*頁\s*$", "", text, flags=re.MULTILINE)

        # 修正中文標點
        text = text.replace("。 ", "。\n")

        return text.strip()

    def to_crawler_result(
        self,
        document: PDFDocument,
        source_url: str,
        source_name: str = "PDF Document",
    ) -> CrawlerResult:
        """
        轉換為 CrawlerResult 格式

        Args:
            document: PDFDocument 結構
            source_url: 來源 URL
            source_name: 來源名稱

        Returns:
            CrawlerResult 結構
        """
        return CrawlerResult(
            status="success",
            source_name=source_name,
            source_url=source_url,
            content=document.full_text,
            content_type="pdf",
            metadata={
                "filename": document.filename,
                "total_pages": document.total_pages,
                "parsed_pages": len(document.pages),
                "table_count": len(document.all_tables),
                "pdf_metadata": document.metadata,
            },
        )


# 便捷函數
async def parse_pdf_url(url: str, max_pages: Optional[int] = None) -> PDFDocument:
    """
    從 URL 解析 PDF 的便捷函數

    Args:
        url: PDF URL
        max_pages: 最大頁數

    Returns:
        PDFDocument
    """
    parser = PDFParser(max_pages=max_pages)
    return await parser.parse_from_url(url)


def parse_pdf_file(filepath: str | Path, max_pages: Optional[int] = None) -> PDFDocument:
    """
    從本地檔案解析 PDF 的便捷函數

    Args:
        filepath: 檔案路徑
        max_pages: 最大頁數

    Returns:
        PDFDocument
    """
    parser = PDFParser(max_pages=max_pages)
    return parser.parse_from_file(filepath)
