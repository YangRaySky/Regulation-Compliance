#!/bin/bash

# 資安法規合規代理人系統 - 啟動腳本
# 確保使用專案內的虛擬環境

echo "🚀 啟動資安法規合規代理人系統..."
echo ""

# 檢查虛擬環境是否存在
if [ ! -d ".venv" ]; then
    echo "❌ 找不到虛擬環境 (.venv)"
    echo "請先建立虛擬環境："
    echo "  python3 -m venv .venv"
    echo "  .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# 檢查必要套件是否已安裝
if ! .venv/bin/python -c "import gradio" 2>/dev/null; then
    echo "❌ Gradio 未安裝"
    echo "請執行："
    echo "  .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# 確認 .env 檔案存在
if [ ! -f ".env" ]; then
    echo "⚠️  警告：找不到 .env 檔案"
    echo "請建立 .env 並設定以下變數："
    echo "  AZURE_OPENAI_ENDPOINT"
    echo "  AZURE_OPENAI_API_KEY"
    echo "  AZURE_OPENAI_GPT5_DEPLOYMENT"
    echo ""
fi

# 啟動應用程式
echo "✅ 使用專案虛擬環境啟動..."
echo "📂 虛擬環境: $(pwd)/.venv"
echo ""

.venv/bin/python app.py
