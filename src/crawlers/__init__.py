"""
爬蟲模組

提供各法規資料來源的爬蟲實作。

支援功能：
- 網頁爬取 (HTML 解析)
- PDF 文件下載與解析
- 結構化資料提取
"""

from .base import BaseCrawler, CrawlerResult
from .tw_laws import TaiwanLawsCrawler
from .pdf_parser import (
    PDFParser,
    PDFDocument,
    PDFPage,
    parse_pdf_url,
    parse_pdf_file,
)

__all__ = [
    # 基礎類別
    "BaseCrawler",
    "CrawlerResult",
    # 台灣法規爬蟲
    "TaiwanLawsCrawler",
    # PDF 解析
    "PDFParser",
    "PDFDocument",
    "PDFPage",
    "parse_pdf_url",
    "parse_pdf_file",
]
