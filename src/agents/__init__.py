"""
Agent 模組

提供 AI 模型客戶端和 LangGraph 多 Agent 團隊：
- BaseLLMClient: LLM 客戶端基底類別（共用功能）
- ClaudeClient: Claude claude-opus-4-5 (Anthropic Foundry on Azure)
- GPTClient: GPT-5.1 (Azure OpenAI)
- RegulationAgentTeam: LangGraph 多 Agent 協作團隊
"""

from ..utils.config import validate_config
from .base_client import BaseLLMClient, LLMResponse
from .claude_client import ClaudeClient, get_claude_client
from .gpt_client import GPTClient, get_gpt_client
from .tools import AVAILABLE_TOOLS, get_tool_descriptions

# LangGraph 多 Agent 團隊
from .langgraph_team import (
    RegulationAgentTeam,
    get_agent_team,
    reset_agent_team,
)

__all__ = [
    # 配置
    "validate_config",
    # AI 客戶端基底類別
    "BaseLLMClient",
    "LLMResponse",
    # AI 客戶端
    "ClaudeClient",
    "get_claude_client",
    "GPTClient",
    "get_gpt_client",
    # LangGraph Agent 團隊
    "RegulationAgentTeam",
    "get_agent_team",
    "reset_agent_team",
    # 工具
    "AVAILABLE_TOOLS",
    "get_tool_descriptions",
]
