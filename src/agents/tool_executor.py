"""
工具執行器

負責根據 Function Calling 的 tool_calls 執行對應的工具函數。
"""

import json
from typing import Any

from .tools import (
    web_search,
    search_tw_laws,
    fetch_tw_law_content,
    fetch_webpage,
    fetch_pdf_content,
    search_jp_laws,
    search_eu_laws,
)


# 工具註冊表：名稱 -> 函數
TOOL_REGISTRY: dict[str, callable] = {
    "web_search": web_search,
    "search_tw_laws": search_tw_laws,
    "fetch_tw_law_content": fetch_tw_law_content,
    "fetch_webpage": fetch_webpage,
    "fetch_pdf_content": fetch_pdf_content,
    "search_jp_laws": search_jp_laws,
    "search_eu_laws": search_eu_laws,
}


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """
    執行指定工具並返回結果

    Args:
        name: 工具名稱
        arguments: 工具參數（已解析的 dict）

    Returns:
        JSON 格式的執行結果字串
    """
    if name not in TOOL_REGISTRY:
        return json.dumps({
            "status": "error",
            "error": f"未知工具: {name}",
            "available_tools": list(TOOL_REGISTRY.keys())
        }, ensure_ascii=False)

    try:
        func = TOOL_REGISTRY[name]
        result = func(**arguments)
        return result
    except TypeError as e:
        # 參數錯誤
        return json.dumps({
            "status": "error",
            "error": f"工具參數錯誤: {str(e)}",
            "tool": name,
            "provided_arguments": arguments
        }, ensure_ascii=False)
    except Exception as e:
        # 其他執行錯誤
        return json.dumps({
            "status": "error",
            "error": f"工具執行失敗: {str(e)}",
            "tool": name
        }, ensure_ascii=False)


def execute_tool_call(tool_call) -> dict:
    """
    執行 LangChain 格式的 tool_call

    Args:
        tool_call: LangChain 的 ToolCall 物件，包含 name, args, id

    Returns:
        包含 tool_call_id 和 content 的字典，可直接用於構建 ToolMessage
    """
    name = tool_call.get("name") if isinstance(tool_call, dict) else tool_call.name

    # 解析 arguments
    if isinstance(tool_call, dict):
        args = tool_call.get("args", {})
    else:
        args = tool_call.args if hasattr(tool_call, "args") else {}

    # 如果 args 是字串，嘗試解析 JSON
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}

    # 執行工具
    result = execute_tool(name, args)

    # 取得 tool_call_id
    if isinstance(tool_call, dict):
        tool_call_id = tool_call.get("id", "")
    else:
        tool_call_id = tool_call.id if hasattr(tool_call, "id") else ""

    return {
        "tool_call_id": tool_call_id,
        "content": result,
        "name": name
    }


def parse_tool_results(result_str: str) -> list[dict]:
    """
    解析工具執行結果，提取搜尋結果列表

    Args:
        result_str: 工具返回的 JSON 字串

    Returns:
        解析後的結果列表
    """
    try:
        result_data = json.loads(result_str)

        if isinstance(result_data, dict):
            if result_data.get("status") == "error":
                return []

            # 嘗試提取 results 欄位
            if "results" in result_data:
                return result_data["results"]

            # 對於 fetch_tw_law_content 等返回單一結果的工具
            return [result_data]

        if isinstance(result_data, list):
            return result_data

        return []

    except json.JSONDecodeError:
        return []


def get_available_tools() -> list[str]:
    """取得所有可用工具名稱"""
    return list(TOOL_REGISTRY.keys())
