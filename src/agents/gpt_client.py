"""
GPT-5.1 (Azure OpenAI) 客戶端

透過 Azure OpenAI 呼叫 GPT-5.1 模型。
繼承 BaseLLMClient 以獲得共用功能。
"""

import os
from typing import Optional
from dataclasses import dataclass

from openai import AzureOpenAI
from dotenv import load_dotenv

from .base_client import BaseLLMClient, LLMResponse

load_dotenv()


@dataclass
class GPTResponse:
    """GPT 回應結構（保留向後相容）"""
    content: str
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[dict] = None


class GPTClient(BaseLLMClient):
    """
    GPT-5.1 客戶端

    使用 Azure OpenAI API 呼叫 GPT-5.1 模型。
    繼承 BaseLLMClient 以獲得 analyze_query 和 search_regulations 方法。
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        """
        初始化 GPT 客戶端

        Args:
            endpoint: Azure OpenAI 端點 URL
            api_key: API 金鑰
            deployment: 部署名稱
            api_version: API 版本
        """
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_GPT5_DEPLOYMENT", "gpt-5.1")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

        if not self.endpoint or not self.api_key:
            raise ValueError("AZURE_OPENAI_ENDPOINT 和 AZURE_OPENAI_API_KEY 必須設定")

        self._client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
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
            max_tokens: 最大完成 token 數

        Returns:
            LLMResponse 物件
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": message})

        response = self._client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            max_completion_tokens=max_tokens,
        )

        choice = response.choices[0] if response.choices else None
        content = choice.message.content if choice else ""

        return LLMResponse(
            content=content,
            model=response.model,
            finish_reason=choice.finish_reason if choice else None,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else None,
        )

    # analyze_query 和 search_regulations 繼承自 BaseLLMClient


# 全域實例
_gpt_client: Optional[GPTClient] = None


def get_gpt_client() -> GPTClient:
    """取得 GPT 客戶端實例"""
    global _gpt_client
    if _gpt_client is None:
        _gpt_client = GPTClient()
    return _gpt_client
