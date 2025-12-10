"""
工具模組單元測試

測試 src/agents/tools.py 的功能。
使用 mock 避免實際網路請求。
"""

import pytest
import inspect
from unittest.mock import patch, MagicMock

from src.agents.tools import (
    AVAILABLE_TOOLS,
    get_tool_descriptions,
    web_search,
    search_tw_laws,
    fetch_tw_law_content,
    fetch_webpage,
    fetch_pdf_content,
    search_jp_laws,
    search_eu_laws,
)


class TestToolsMetadata:
    """工具元資料測試"""

    def test_available_tools_is_list(self):
        """測試 AVAILABLE_TOOLS 是列表"""
        assert isinstance(AVAILABLE_TOOLS, list)

    def test_available_tools_has_items(self):
        """測試 AVAILABLE_TOOLS 包含工具"""
        assert len(AVAILABLE_TOOLS) > 0

    def test_each_tool_is_callable(self):
        """測試每個工具都是可呼叫的"""
        for tool in AVAILABLE_TOOLS:
            assert callable(tool), f"工具 {tool} 不是可呼叫的"

    def test_available_tools_contains_required_functions(self):
        """測試包含必要的工具函數"""
        tool_names = [tool.__name__ for tool in AVAILABLE_TOOLS]

        required_tools = [
            "web_search",
            "search_tw_laws",
            "fetch_tw_law_content",
            "fetch_webpage",
        ]

        for tool in required_tools:
            assert tool in tool_names, f"缺少工具: {tool}"

    def test_get_tool_descriptions_returns_string(self):
        """測試 get_tool_descriptions 返回字串"""
        descriptions = get_tool_descriptions()
        assert isinstance(descriptions, str)
        assert len(descriptions) > 0

    def test_get_tool_descriptions_contains_tool_info(self):
        """測試描述包含工具資訊"""
        descriptions = get_tool_descriptions()

        # 應該包含一些工具相關的關鍵字
        assert "search" in descriptions.lower() or "法規" in descriptions


class TestWebSearchTool:
    """web_search 工具測試"""

    def test_web_search_function_exists(self):
        """測試 web_search 函數存在且可呼叫"""
        assert callable(web_search)

    def test_web_search_has_docstring(self):
        """測試 web_search 有文檔字串"""
        assert web_search.__doc__ is not None
        assert len(web_search.__doc__) > 0

    def test_web_search_accepts_query_parameter(self):
        """測試 web_search 接受 query 參數"""
        sig = inspect.signature(web_search)
        params = list(sig.parameters.keys())
        assert 'query' in params or len(params) > 0


class TestTaiwanLawsTools:
    """台灣法規工具測試"""

    def test_search_tw_laws_is_callable(self):
        """測試 search_tw_laws 是可呼叫的"""
        assert callable(search_tw_laws)

    def test_fetch_tw_law_content_is_callable(self):
        """測試 fetch_tw_law_content 是可呼叫的"""
        assert callable(fetch_tw_law_content)


class TestFetchTools:
    """內容擷取工具測試"""

    def test_fetch_webpage_is_callable(self):
        """測試 fetch_webpage 是可呼叫的"""
        assert callable(fetch_webpage)

    def test_fetch_pdf_content_is_callable(self):
        """測試 fetch_pdf_content 是可呼叫的"""
        assert callable(fetch_pdf_content)

    @patch('src.agents.tools.httpx.get')
    def test_fetch_webpage_handles_error(self, mock_get):
        """測試 fetch_webpage 錯誤處理"""
        mock_get.side_effect = Exception("Connection error")

        result = fetch_webpage("https://invalid-url.com")

        # 應該返回錯誤訊息而不是拋出異常
        assert isinstance(result, (str, dict))


class TestJapanLawsTools:
    """日本法規工具測試"""

    def test_search_jp_laws_is_callable(self):
        """測試 search_jp_laws 是可呼叫的"""
        assert callable(search_jp_laws)


class TestEuLawsTools:
    """歐盟法規工具測試"""

    def test_search_eu_laws_is_callable(self):
        """測試 search_eu_laws 是可呼叫的"""
        assert callable(search_eu_laws)


class TestUrlValidation:
    """URL 驗證安全性測試（防止 SSRF 攻擊）"""

    def test_fetch_webpage_rejects_localhost(self):
        """測試 fetch_webpage 拒絕 localhost"""
        import json
        result = fetch_webpage("http://localhost:8080/test")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "本地網址" in result_data["error"]

    def test_fetch_webpage_rejects_127_0_0_1(self):
        """測試 fetch_webpage 拒絕 127.0.0.1"""
        import json
        result = fetch_webpage("http://127.0.0.1/test")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "本地網址" in result_data["error"]

    def test_fetch_webpage_rejects_private_ip_192(self):
        """測試 fetch_webpage 拒絕內網 IP 192.168.x.x"""
        import json
        result = fetch_webpage("http://192.168.1.1/admin")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "私有 IP" in result_data["error"] or "內部網路" in result_data["error"]

    def test_fetch_webpage_rejects_private_ip_10(self):
        """測試 fetch_webpage 拒絕內網 IP 10.x.x.x"""
        import json
        result = fetch_webpage("http://10.0.0.1/secret")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "私有 IP" in result_data["error"] or "內部網路" in result_data["error"]

    def test_fetch_webpage_rejects_private_ip_172(self):
        """測試 fetch_webpage 拒絕內網 IP 172.16.x.x"""
        import json
        result = fetch_webpage("http://172.16.0.1/internal")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "私有 IP" in result_data["error"] or "內部網路" in result_data["error"]

    def test_fetch_webpage_rejects_file_protocol(self):
        """測試 fetch_webpage 拒絕 file:// 協議"""
        import json
        result = fetch_webpage("file:///etc/passwd")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "不支援的協議" in result_data["error"]

    def test_fetch_webpage_rejects_ftp_protocol(self):
        """測試 fetch_webpage 拒絕 ftp:// 協議"""
        import json
        result = fetch_webpage("ftp://ftp.example.com/file.txt")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "不支援的協議" in result_data["error"]

    def test_fetch_pdf_rejects_localhost(self):
        """測試 fetch_pdf_content 拒絕 localhost"""
        import json
        result = fetch_pdf_content("http://localhost/test.pdf")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "本地網址" in result_data["error"]

    def test_fetch_pdf_rejects_private_ip(self):
        """測試 fetch_pdf_content 拒絕內網 IP"""
        import json
        result = fetch_pdf_content("http://192.168.1.100/secret.pdf")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "私有 IP" in result_data["error"] or "內部網路" in result_data["error"]

    def test_fetch_pdf_rejects_file_protocol(self):
        """測試 fetch_pdf_content 拒絕 file:// 協議"""
        import json
        result = fetch_pdf_content("file:///home/user/secret.pdf")
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "不支援的協議" in result_data["error"]
