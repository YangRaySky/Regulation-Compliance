"""
工具 JSON Schema 定義測試
"""

from src.agents.tool_schemas import (
    TOOL_SCHEMAS,
    get_tool_names,
    get_tool_schema_by_name,
    get_tool_schemas,
)


class TestToolSchemas:
    """測試 TOOL_SCHEMAS 結構"""

    def test_tool_schemas_is_list(self):
        """TOOL_SCHEMAS 應該是 list"""
        assert isinstance(TOOL_SCHEMAS, list)

    def test_tool_schemas_not_empty(self):
        """TOOL_SCHEMAS 不應該是空的"""
        assert len(TOOL_SCHEMAS) > 0

    def test_all_tools_have_required_fields(self):
        """每個工具都應該有必要欄位（OpenAI 格式：type + function 包裝）"""
        for tool in TOOL_SCHEMAS:
            assert "type" in tool, "工具缺少 type 欄位"
            assert "function" in tool, "工具缺少 function 欄位"
            func = tool["function"]
            required_fields = {"name", "description", "parameters"}
            assert required_fields.issubset(func.keys()), f"{func.get('name', 'unknown')} 缺少必要欄位"

    def test_all_tools_have_valid_type(self):
        """每個工具的 type 應該是 'function'"""
        for tool in TOOL_SCHEMAS:
            assert tool["type"] == "function", "type 應為 'function'"

    def test_all_tools_have_parameters_object(self):
        """每個工具的 parameters 應該是 object 類型"""
        for tool in TOOL_SCHEMAS:
            func = tool["function"]
            params = func["parameters"]
            assert params["type"] == "object", f"{func['name']} 的 parameters.type 應為 'object'"

    def test_all_tools_have_required_array(self):
        """每個工具的 parameters 應該有 required 陣列"""
        for tool in TOOL_SCHEMAS:
            func = tool["function"]
            assert "required" in func["parameters"], f"{func['name']} 缺少 required 欄位"
            assert isinstance(func["parameters"]["required"], list)

    def test_expected_tools_exist(self):
        """應該包含所有預期的工具"""
        expected_tools = {
            "web_search",
            "search_tw_laws",
            "fetch_tw_law_content",
            "fetch_webpage",
            "fetch_pdf_content",
            "search_jp_laws",
            "search_eu_laws",
        }
        actual_tools = {tool["function"]["name"] for tool in TOOL_SCHEMAS}
        assert expected_tools == actual_tools


class TestGetToolSchemas:
    """測試 get_tool_schemas 函數"""

    def test_returns_list(self):
        """應該返回 list"""
        result = get_tool_schemas()
        assert isinstance(result, list)

    def test_returns_same_as_constant(self):
        """應該返回與 TOOL_SCHEMAS 相同的內容"""
        result = get_tool_schemas()
        assert result == TOOL_SCHEMAS


class TestGetToolNames:
    """測試 get_tool_names 函數"""

    def test_returns_list(self):
        """應該返回 list"""
        result = get_tool_names()
        assert isinstance(result, list)

    def test_returns_all_tool_names(self):
        """應該返回所有工具名稱"""
        result = get_tool_names()
        assert len(result) == len(TOOL_SCHEMAS)
        for name in result:
            assert isinstance(name, str)

    def test_contains_expected_names(self):
        """應該包含預期的工具名稱"""
        result = get_tool_names()
        assert "web_search" in result
        assert "search_tw_laws" in result
        assert "fetch_webpage" in result


class TestGetToolSchemaByName:
    """測試 get_tool_schema_by_name 函數"""

    def test_returns_correct_schema(self):
        """應該返回正確的 schema"""
        result = get_tool_schema_by_name("web_search")
        assert result is not None
        assert result["function"]["name"] == "web_search"

    def test_returns_none_for_unknown_tool(self):
        """對於不存在的工具應該返回 None"""
        result = get_tool_schema_by_name("nonexistent_tool")
        assert result is None

    def test_web_search_schema_structure(self):
        """web_search 的 schema 應該有正確結構"""
        schema = get_tool_schema_by_name("web_search")
        assert schema is not None
        func = schema["function"]
        assert "query" in func["parameters"]["properties"]
        assert "region" in func["parameters"]["properties"]
        assert "num_results" in func["parameters"]["properties"]
        assert "query" in func["parameters"]["required"]

    def test_search_tw_laws_schema_structure(self):
        """search_tw_laws 的 schema 應該有正確結構"""
        schema = get_tool_schema_by_name("search_tw_laws")
        assert schema is not None
        func = schema["function"]
        assert "query" in func["parameters"]["properties"]
        assert "limit" in func["parameters"]["properties"]
        assert "query" in func["parameters"]["required"]
