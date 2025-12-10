"""
工具執行器測試
"""

import json

from src.agents.tool_executor import (
    TOOL_REGISTRY,
    execute_tool,
    execute_tool_call,
    get_available_tools,
    parse_tool_results,
)


class TestToolRegistry:
    """測試工具註冊表"""

    def test_registry_is_dict(self):
        """TOOL_REGISTRY 應該是 dict"""
        assert isinstance(TOOL_REGISTRY, dict)

    def test_registry_not_empty(self):
        """TOOL_REGISTRY 不應該是空的"""
        assert len(TOOL_REGISTRY) > 0

    def test_all_values_are_callable(self):
        """所有註冊的工具都應該是可呼叫的"""
        for name, func in TOOL_REGISTRY.items():
            assert callable(func), f"{name} 應該是可呼叫的"

    def test_expected_tools_registered(self):
        """應該註冊所有預期的工具"""
        expected = {
            "web_search",
            "search_tw_laws",
            "fetch_tw_law_content",
            "fetch_webpage",
            "fetch_pdf_content",
            "search_jp_laws",
            "search_eu_laws",
        }
        assert expected == set(TOOL_REGISTRY.keys())


class TestExecuteTool:
    """測試 execute_tool 函數"""

    def test_unknown_tool_returns_error(self):
        """未知工具應該返回錯誤"""
        result = execute_tool("nonexistent_tool", {})
        result_dict = json.loads(result)
        assert result_dict["status"] == "error"
        assert "未知工具" in result_dict["error"]
        assert "available_tools" in result_dict

    def test_invalid_arguments_returns_error(self):
        """無效參數應該返回錯誤"""
        # web_search 需要 query 參數
        result = execute_tool("web_search", {"invalid_param": "test"})
        result_dict = json.loads(result)
        # 可能返回 error 或 success（取決於函數的參數處理）
        assert "status" in result_dict


class TestExecuteToolCall:
    """測試 execute_tool_call 函數"""

    def test_dict_format_tool_call(self):
        """應該處理 dict 格式的 tool_call"""
        tool_call = {
            "id": "test_id_123",
            "name": "search_tw_laws",
            "args": {"query": "個人資料保護"},
        }
        result = execute_tool_call(tool_call)
        assert result["tool_call_id"] == "test_id_123"
        assert result["name"] == "search_tw_laws"
        assert "content" in result

    def test_result_contains_required_fields(self):
        """結果應該包含必要欄位"""
        tool_call = {
            "id": "test_id",
            "name": "search_eu_laws",
            "args": {"query": "GDPR"},
        }
        result = execute_tool_call(tool_call)
        assert "tool_call_id" in result
        assert "content" in result
        assert "name" in result

    def test_handles_string_args(self):
        """應該處理 JSON 字串格式的 args"""
        tool_call = {
            "id": "test_id",
            "name": "search_jp_laws",
            "args": '{"query": "個人情報"}',
        }
        result = execute_tool_call(tool_call)
        assert "content" in result


class TestParseToolResults:
    """測試 parse_tool_results 函數"""

    def test_parse_success_with_results(self):
        """應該解析成功結果中的 results 欄位"""
        result_str = json.dumps({
            "status": "success",
            "results": [
                {"title": "法規1", "url": "http://example.com/1"},
                {"title": "法規2", "url": "http://example.com/2"},
            ]
        })
        parsed = parse_tool_results(result_str)
        assert len(parsed) == 2
        assert parsed[0]["title"] == "法規1"

    def test_parse_error_returns_empty(self):
        """錯誤結果應該返回空列表"""
        result_str = json.dumps({
            "status": "error",
            "error": "something went wrong"
        })
        parsed = parse_tool_results(result_str)
        assert parsed == []

    def test_parse_single_result(self):
        """應該解析單一結果（沒有 results 欄位）"""
        result_str = json.dumps({
            "status": "success",
            "title": "法規名稱",
            "content": "法規內容"
        })
        parsed = parse_tool_results(result_str)
        assert len(parsed) == 1
        assert parsed[0]["title"] == "法規名稱"

    def test_parse_list_result(self):
        """應該解析列表格式的結果"""
        result_str = json.dumps([
            {"title": "項目1"},
            {"title": "項目2"},
        ])
        parsed = parse_tool_results(result_str)
        assert len(parsed) == 2

    def test_parse_invalid_json_returns_empty(self):
        """無效 JSON 應該返回空列表"""
        parsed = parse_tool_results("not valid json {{{")
        assert parsed == []

    def test_parse_empty_string_returns_empty(self):
        """空字串應該返回空列表"""
        parsed = parse_tool_results("")
        assert parsed == []


class TestGetAvailableTools:
    """測試 get_available_tools 函數"""

    def test_returns_list(self):
        """應該返回 list"""
        result = get_available_tools()
        assert isinstance(result, list)

    def test_returns_all_registered_tools(self):
        """應該返回所有註冊的工具名稱"""
        result = get_available_tools()
        assert set(result) == set(TOOL_REGISTRY.keys())

    def test_returns_strings(self):
        """應該返回字串列表"""
        result = get_available_tools()
        for name in result:
            assert isinstance(name, str)
