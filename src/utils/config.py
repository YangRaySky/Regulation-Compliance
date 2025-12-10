"""
設定模組

提供環境變數與設定檔讀取功能。
"""

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()


def get_env(
    key: str,
    default: Any = None,
    required: bool = False,
) -> Any:
    """
    取得環境變數

    Args:
        key: 環境變數名稱
        default: 預設值
        required: 是否為必要變數

    Returns:
        環境變數值

    Raises:
        ValueError: 若 required=True 但變數不存在
    """
    value = os.getenv(key, default)

    if required and value is None:
        raise ValueError(f"必要的環境變數 '{key}' 未設定")

    return value


def load_config(config_path: str) -> dict:
    """
    載入 YAML 設定檔

    Args:
        config_path: 設定檔路徑

    Returns:
        設定字典

    Raises:
        FileNotFoundError: 若設定檔不存在
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"設定檔不存在: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_prompt(prompt_name: str) -> str:
    """
    載入 System Prompt 檔案

    Args:
        prompt_name: Prompt 名稱 (不含副檔名)

    Returns:
        Prompt 內容
    """
    # 嘗試不同的路徑
    possible_paths = [
        Path(f"config/prompts/{prompt_name}.md"),
        Path(f"../config/prompts/{prompt_name}.md"),
        Path(__file__).parent.parent.parent / "config" / "prompts" / f"{prompt_name}.md",
    ]

    for path in possible_paths:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

    raise FileNotFoundError(f"找不到 Prompt 檔案: {prompt_name}.md")


class Config:
    """
    應用程式設定類別

    集中管理所有設定值。
    """

    def __init__(self):
        """初始化設定"""
        self._load_env()

    def _load_env(self):
        """從環境變數載入設定"""
        # Azure OpenAI 設定
        self.azure_openai_api_key = get_env("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = get_env("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_version = get_env(
            "AZURE_OPENAI_API_VERSION",
            "2024-02-15-preview"
        )
        self.azure_openai_gpt4o_deployment = get_env(
            "AZURE_OPENAI_GPT4O_DEPLOYMENT",
            "gpt-4o"
        )
        self.azure_openai_gpt4o_mini_deployment = get_env(
            "AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT",
            "gpt-4o-mini"
        )

        # 應用程式設定
        self.app_env = get_env("APP_ENV", "development")
        self.log_level = get_env("LOG_LEVEL", "INFO")

        # 資料庫設定
        self.database_url = get_env(
            "DATABASE_URL",
            "sqlite:///./data/regulations.db"
        )
        self.chroma_persist_directory = get_env(
            "CHROMA_PERSIST_DIRECTORY",
            "./data/chroma"
        )

        # Web UI 設定
        self.gradio_server_port = int(get_env("GRADIO_SERVER_PORT", "7860"))
        self.gradio_server_name = get_env("GRADIO_SERVER_NAME", "0.0.0.0")

    @property
    def is_development(self) -> bool:
        """是否為開發環境"""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """是否為生產環境"""
        return self.app_env == "production"

    def validate(self) -> list[str]:
        """
        驗證設定是否完整

        Returns:
            缺少的必要設定列表
        """
        missing = []

        if not self.azure_openai_api_key:
            missing.append("AZURE_OPENAI_API_KEY")

        if not self.azure_openai_endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")

        return missing


# 全域設定實例
_config: Optional[Config] = None


def get_config() -> Config:
    """取得全域設定實例"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def validate_config() -> bool:
    """
    驗證環境變數設定是否完整

    檢查 Azure OpenAI 或 Anthropic Foundry 至少有一組設定完整。

    Returns:
        True 如果設定完整，否則 False
    """
    # 檢查 Azure OpenAI 設定
    azure_openai_ok = bool(
        os.getenv("AZURE_OPENAI_API_KEY") and
        os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    # 檢查 Anthropic Foundry 設定
    anthropic_ok = bool(
        os.getenv("ANTHROPIC_FOUNDRY_API_KEY") and
        os.getenv("ANTHROPIC_FOUNDRY_ENDPOINT")
    )

    if not azure_openai_ok and not anthropic_ok:
        print("缺少必要的環境變數:")
        print("  - Azure OpenAI: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT")
        print("  - 或 Anthropic Foundry: ANTHROPIC_FOUNDRY_API_KEY, ANTHROPIC_FOUNDRY_ENDPOINT")
        print("請參考 .env.example 設定環境變數")
        return False

    return True
