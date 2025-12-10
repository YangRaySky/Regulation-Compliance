"""
資安合規代理人系統 - Web UI 入口

使用 Gradio 建立的簡易 Web 介面。
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 使用簡化版 UI 以避免 Gradio JSON schema bug
from src.ui.simple_ui import launch_simple_app


def main():
    """主程式入口"""
    # 從環境變數取得設定
    server_name = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
    server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    share = os.getenv("GRADIO_SHARE", "false").lower() == "true"

    print("=" * 60)
    print("🔒 資安法規合規代理人系統（簡化版 UI）")
    print("=" * 60)
    print(f"📍 伺服器: http://{server_name}:{server_port}")
    print(f"🌐 公開分享: {'是' if share else '否'}")
    print("=" * 60)
    print()

    # 啟動應用程式（使用簡化版 UI）
    launch_simple_app(
        server_name=server_name,
        server_port=server_port,
        share=share,
    )


if __name__ == "__main__":
    main()
