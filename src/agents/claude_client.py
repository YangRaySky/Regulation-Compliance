"""
Claude (Anthropic Foundry on Azure) 客戶端

透過 Azure AI Services 的 Anthropic Foundry 呼叫 Claude 模型。
繼承 BaseLLMClient 以獲得共用功能。
"""

import os
from typing import Optional
from dataclasses import dataclass

from anthropic import AnthropicFoundry
from dotenv import load_dotenv

from .base_client import BaseLLMClient, LLMResponse

load_dotenv()


@dataclass
class ClaudeResponse:
    """Claude 回應結構（保留向後相容）"""
    content: str
    model: str
    stop_reason: Optional[str] = None
    usage: Optional[dict] = None


class ClaudeClient(BaseLLMClient):
    """
    Claude 客戶端

    使用 Anthropic Foundry API 在 Azure AI Services 上呼叫 Claude 模型。
    繼承 BaseLLMClient 以獲得 analyze_query 和 search_regulations 方法。
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        初始化 Claude 客戶端

        Args:
            endpoint: Anthropic Foundry 端點 URL
            api_key: API 金鑰
            model: 模型名稱（部署名稱）
        """
        self.endpoint = endpoint or os.getenv("ANTHROPIC_FOUNDRY_ENDPOINT")
        self.api_key = api_key or os.getenv("ANTHROPIC_FOUNDRY_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_FOUNDRY_MODEL", "claude-opus-4-5")

        if not self.endpoint or not self.api_key:
            raise ValueError("ANTHROPIC_FOUNDRY_ENDPOINT 和 ANTHROPIC_FOUNDRY_API_KEY 必須設定")

        self._client = AnthropicFoundry(
            api_key=self.api_key,
            base_url=self.endpoint,
        )

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """
        發送聊天訊息

        Args:
            message: 使用者訊息
            system_prompt: 系統提示詞
            max_tokens: 最大 token 數

        Returns:
            LLMResponse 物件
        """
        messages = [{"role": "user", "content": message}]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)

        # 提取文字內容
        content = ""
        if response.content:
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

        return LLMResponse(
            content=content,
            model=response.model,
            finish_reason=response.stop_reason,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            } if response.usage else None,
        )

    # analyze_query 和 search_regulations 繼承自 BaseLLMClient


# 全域實例
_claude_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """取得 Claude 客戶端實例"""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client
