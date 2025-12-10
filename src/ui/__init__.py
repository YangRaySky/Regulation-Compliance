"""
Web UI 模組

使用 Gradio 建立簡易 Web 介面。
"""

# 只導入必要的模組，避免自動載入 components.py 造成 Gradio bug
from .handlers import RegulationQueryHandler

__all__ = [
    "RegulationQueryHandler",
]

# components.create_app 和 simple_ui.launch_simple_app 需要時才手動導入
