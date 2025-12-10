"""
測試 LLM 連接 - Azure OpenAI 和 Anthropic Foundry

在報告模型問題之前，先使用此腳本測試連接。
"""

import os

import pytest
from dotenv import load_dotenv

load_dotenv()


def test_azure_openai():
    """測試 Azure OpenAI GPT-5.1"""
    from openai import AzureOpenAI

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_GPT5_DEPLOYMENT", "gpt-5.1")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    # 跳過 CI 環境或未配置的情況
    if not endpoint or not api_key or api_key.startswith("test-"):
        pytest.skip("Azure OpenAI 未配置或為 CI 測試環境")

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )

    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": "Say 'OK'"}
        ],
        max_completion_tokens=10,
        model=deployment
    )

    assert response.choices[0].message.content is not None


def test_anthropic_foundry():
    """測試 Anthropic Foundry Claude"""
    from anthropic import AnthropicFoundry

    endpoint = os.getenv("ANTHROPIC_FOUNDRY_ENDPOINT")
    api_key = os.getenv("ANTHROPIC_FOUNDRY_API_KEY")
    deployment = os.getenv("ANTHROPIC_FOUNDRY_DEPLOYMENT", "claude-opus-4-5")

    if not endpoint or not api_key:
        pytest.skip("Anthropic Foundry 未配置")

    client = AnthropicFoundry(
        api_key=api_key,
        base_url=endpoint
    )

    message = client.messages.create(
        model=deployment,
        messages=[
            {"role": "user", "content": "Say 'OK'"}
        ],
        max_tokens=10,
    )

    assert message.content is not None


def test_langgraph_llm():
    """測試 LangGraph LLM 配置"""
    # 跳過 CI 環境
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key or api_key.startswith("test-"):
        pytest.skip("CI 測試環境，跳過 LLM 連線測試")

    from src.agents.langgraph_team import get_llm

    llm = get_llm()
    assert llm is not None

    response = llm.invoke("Say 'OK'")
    assert response.content is not None


if __name__ == "__main__":
    print("\n🧪 開始測試 LLM 連接...\n")

    print("=" * 60)
    print("測試 Azure OpenAI GPT-5.1")
    print("=" * 60)
    try:
        test_azure_openai()
        print("✅ Azure OpenAI 連接成功！")
    except Exception as e:
        print(f"❌ Azure OpenAI 連接失敗: {e}")

    print()
    print("=" * 60)
    print("測試 Anthropic Foundry Claude")
    print("=" * 60)
    try:
        test_anthropic_foundry()
        print("✅ Anthropic Foundry 連接成功！")
    except Exception as e:
        print(f"❌ Anthropic Foundry 連接失敗: {e}")

    print()
    print("=" * 60)
    print("測試 LangGraph LLM")
    print("=" * 60)
    try:
        test_langgraph_llm()
        print("✅ LangGraph LLM 配置成功！")
    except Exception as e:
        print(f"❌ LangGraph LLM 配置失敗: {e}")
