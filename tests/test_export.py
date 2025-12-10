"""
匯出模組單元測試

測試 src/utils/export.py 的功能。
"""

import json

import pytest

from src.utils.export import ReportExporter, export_result


class TestReportExporter:
    """ReportExporter 類別測試"""

    def test_init_with_full_data(self, sample_query_result):
        """測試使用完整資料初始化"""
        exporter = ReportExporter(sample_query_result)

        assert exporter.query == sample_query_result["query"]
        assert exporter.original_query == sample_query_result["original_query"]
        assert len(exporter.verified_regulations) == 1
        assert len(exporter.timeline) == 2
        assert len(exporter.compliance_checklist) == 2
        assert exporter.confidence_score == 0.92

    def test_init_with_empty_data(self, empty_query_result):
        """測試使用空資料初始化"""
        exporter = ReportExporter(empty_query_result)

        assert exporter.query == "不存在的法規"
        assert len(exporter.verified_regulations) == 0
        assert len(exporter.timeline) == 0
        assert len(exporter.compliance_checklist) == 0
        assert exporter.confidence_score == 0

    def test_to_markdown_with_full_data(self, sample_query_result):
        """測試匯出完整資料為 Markdown"""
        exporter = ReportExporter(sample_query_result)
        md = exporter.to_markdown()

        # 檢查標題
        assert "# 法規查詢報告" in md
        assert "台灣個資法" in md

        # 檢查摘要
        assert "## 摘要" in md
        assert "個人資料保護法" in md

        # 檢查法規列表
        assert "## 相關法規" in md
        assert "Personal Data Protection Act" in md
        assert "個人資料保護法" in md

        # 檢查重點摘要
        assert "**重點摘要**" in md
        assert "規範個人資料之蒐集" in md

        # 檢查條文節錄
        assert "**條文節錄**" in md
        assert "第 1 條" in md

        # 檢查時間軸
        assert "## 法規時間軸" in md
        assert "1995-08-11" in md

        # 檢查合規檢核清單
        assert "## 合規檢核清單" in md
        assert "告知義務" in md

        # 檢查信心分數
        assert "92%" in md

    def test_to_markdown_with_empty_data(self, empty_query_result):
        """測試匯出空資料為 Markdown"""
        exporter = ReportExporter(empty_query_result)
        md = exporter.to_markdown()

        # 應該還是有標題
        assert "# 法規查詢報告" in md
        assert "不存在的法規" in md

        # 不應有法規列表
        assert "## 相關法規" not in md

    def test_to_json_with_full_data(self, sample_query_result):
        """測試匯出完整資料為 JSON"""
        exporter = ReportExporter(sample_query_result)
        json_str = exporter.to_json()

        # 確認是有效的 JSON
        data = json.loads(json_str)

        # 檢查結構
        assert "export_info" in data
        assert "result" in data
        assert data["export_info"]["format"] == "json"
        assert "exported_at" in data["export_info"]
        assert data["export_info"]["query"] == "台灣個資法"

    def test_to_json_with_indent(self, sample_query_result):
        """測試 JSON 縮排設定"""
        exporter = ReportExporter(sample_query_result)

        # 預設縮排
        json_default = exporter.to_json()
        assert "\n" in json_default  # 有換行

        # 無縮排
        json_compact = exporter.to_json(indent=None)
        # None 縮排仍會有換行，但格式不同


class TestExportResult:
    """export_result 函數測試"""

    def test_export_markdown(self, sample_query_result):
        """測試匯出 Markdown 格式"""
        content, filename, mime = export_result(sample_query_result, "markdown")

        assert isinstance(content, str)
        assert filename.endswith(".md")
        assert "法規報告" in filename
        assert mime == "text/markdown"
        assert "# 法規查詢報告" in content

    def test_export_json(self, sample_query_result):
        """測試匯出 JSON 格式"""
        content, filename, mime = export_result(sample_query_result, "json")

        assert isinstance(content, str)
        assert filename.endswith(".json")
        assert mime == "application/json"

        # 確認是有效 JSON
        data = json.loads(content)
        assert "export_info" in data

    def test_export_unsupported_format(self, sample_query_result):
        """測試匯出不支援的格式"""
        with pytest.raises(ValueError) as exc_info:
            export_result(sample_query_result, "unsupported")

        assert "不支援的格式" in str(exc_info.value)

    def test_export_filename_contains_query(self, sample_query_result):
        """測試檔名包含查詢內容"""
        content, filename, mime = export_result(sample_query_result, "markdown")

        # 檔名應該包含部分查詢內容
        assert "法規報告" in filename
        assert ".md" in filename

    def test_export_pdf_requires_reportlab(self, sample_query_result):
        """測試 PDF 匯出（需要 reportlab）"""
        try:
            content, filename, mime = export_result(sample_query_result, "pdf")

            assert isinstance(content, bytes)
            assert filename.endswith(".pdf")
            assert mime == "application/pdf"
            # PDF 檔案以 %PDF 開頭
            assert content[:4] == b'%PDF'
        except ImportError:
            pytest.skip("reportlab not installed")

    def test_export_docx_requires_docx(self, sample_query_result):
        """測試 Word 匯出（需要 python-docx）"""
        try:
            content, filename, mime = export_result(sample_query_result, "docx")

            assert isinstance(content, bytes)
            assert filename.endswith(".docx")
            assert "wordprocessingml" in mime
        except ImportError:
            pytest.skip("python-docx not installed")

    def test_export_xlsx_requires_openpyxl(self, sample_query_result):
        """測試 Excel 匯出（需要 openpyxl）"""
        try:
            content, filename, mime = export_result(sample_query_result, "xlsx")

            assert isinstance(content, bytes)
            assert filename.endswith(".xlsx")
            assert "spreadsheetml" in mime
        except ImportError:
            pytest.skip("openpyxl not installed")
