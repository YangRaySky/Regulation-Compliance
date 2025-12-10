# 資安法規合規代理人系統

多代理人法規蒐集與解析平台，使用 **LangGraph** 框架與 Azure OpenAI。

## 功能特色

- 🔍 **法規查詢與蒐集** - 支援台灣、歐盟、日本、國際標準等多種法規來源
- 📄 **法規結構化解析** - 將法規文本轉換為結構化資料
- ✅ **資料來源驗證** - 自動驗證來源可信度與資料完整性
- 🌍 **多語言翻譯** - 支援繁體中文、簡體中文、英文、日文
- 📤 **多格式匯出** - 支援 Markdown、JSON、PDF、Word、Excel
- 📦 **智慧快取** - 24 小時自動過期，支援強制重新查詢
- 🖥️ **Web UI 介面** - 使用 Gradio 建立的簡易操作介面

## 系統架構 (LangGraph Multi-Agent)

```
┌─────────────────────────────────────────────────────────────┐
│                    Gradio Web UI                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  LangGraph StateGraph                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Planner   │───▶│ Researcher  │───▶│  Validator  │
│ (GPT-5.1)   │    │(GPT + Tools)│    │ (GPT-5.1)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 快速開始

### 1. 環境需求

- Python 3.10+
- Azure OpenAI 存取權限

### 2. 安裝

```bash
# 進入專案目錄
cd regulation-compliance-agent

# 建立虛擬環境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

### 3. 設定

```bash
# 複製環境變數範例
cp .env.example .env

# 編輯 .env 填入您的 API 設定
```

**⚠️ 安全注意事項**：
- **絕對不要**將 `.env` 檔案提交至版本控制系統
- **絕對不要**將任何 API 金鑰或服務帳戶憑證提交至版本控制系統
- 定期輪換您的 API 金鑰

必要的環境變數：

| 變數名稱 | 說明 | 必填 |
|----------|------|------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API 金鑰 | ✅ |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI 端點 | ✅ |
| `AZURE_OPENAI_GPT5_DEPLOYMENT` | 部署名稱 | ✅ |
| `AZURE_OPENAI_API_VERSION` | API 版本 | ✅ |
| `GOOGLE_API_KEY` | Google Custom Search API 金鑰 | 選填 |
| `GOOGLE_SEARCH_ENGINE_ID` | Google 搜尋引擎 ID | 選填 |

### 4. 執行

```bash
# 啟動 Web UI
python app.py

# 或使用啟動腳本
./start.sh
```

開啟瀏覽器訪問 `http://localhost:7860`

### 5. Docker 部署（選用）

```bash
# 使用 Docker Compose 啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

## 專案結構

```
regulation-compliance-agent/
├── app.py                    # Web UI 入口
├── requirements.txt          # Python 依賴
├── pyproject.toml            # 專案配置
├── Dockerfile                # Docker 映像配置
├── docker-compose.yml        # Docker Compose 配置
├── start.sh                  # 啟動腳本
├── config/
│   └── prompts/              # LangGraph Agent Prompts
│       ├── langgraph_planner.md
│       ├── langgraph_researcher.md
│       └── langgraph_validator.md
├── src/
│   ├── agents/               # LangGraph Agent 實作
│   │   ├── langgraph_team.py # 多 Agent 團隊
│   │   ├── tools.py          # Agent 工具函數
│   │   ├── tool_schemas.py   # 工具 JSON Schema
│   │   ├── tool_executor.py  # 工具執行器
│   │   ├── gpt_client.py     # Azure OpenAI 客戶端
│   │   └── claude_client.py  # Claude 客戶端
│   ├── crawlers/             # 法規爬蟲
│   │   ├── base.py           # 爬蟲基礎類別
│   │   ├── tw_laws.py        # 台灣法規爬蟲
│   │   └── pdf_parser.py     # PDF 解析器
│   ├── storage/              # 儲存層介面
│   │   ├── interfaces.py     # 抽象介面
│   │   └── local.py          # 本地儲存實作
│   ├── models/               # Pydantic 資料模型
│   │   └── regulation.py     # 法規資料模型
│   ├── ui/                   # Web UI 元件
│   │   ├── simple_ui.py      # 簡化版 UI
│   │   └── handlers.py       # 事件處理器
│   └── utils/                # 工具模組
│       ├── cache.py          # 查詢快取
│       ├── config.py         # 配置載入
│       ├── conversation.py   # 對話管理
│       ├── export.py         # 匯出功能
│       ├── history.py        # 歷史記錄
│       └── logging.py        # 日誌設定
└── tests/                    # 單元測試
```

## Agent 說明

| Agent | 模型 | 職責 |
|-------|------|------|
| **Planner** | GPT-5.1 | 分析查詢意圖，制定多關鍵字搜尋策略 |
| **Researcher** | GPT-5.1 + Function Calling | 使用 LLM 決策調用工具，執行網頁搜尋、爬蟲、PDF 解析 |
| **Validator** | GPT-5.1 | 驗證結果、提取條文、生成合規檢核清單 |

## 支援的法規來源

### 台灣
- 全國法規資料庫 (law.moj.gov.tw)
- 金管會法規查詢系統
- 數位發展部

### 日本
- e-Gov 法令檢索
- 金融廳 (FSA)

### 歐盟
- EUR-Lex
- GDPR Portal

### 國際標準
- NIST (CSF, 800-53)
- ISO (27001, 27002)
- CIS Controls

## 匯出功能

支援將查詢結果匯出為多種格式：

| 格式 | 副檔名 | 說明 |
|------|--------|------|
| Markdown | `.md` | 純文字格式，適合文檔 |
| JSON | `.json` | 結構化資料，適合系統整合 |
| PDF | `.pdf` | 正式報告格式 |
| Word | `.docx` | Microsoft Word 文件 |
| Excel | `.xlsx` | 試算表格式，含多工作表 |

## 開發

```bash
# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest tests/

# 程式碼格式化
black src/
ruff check src/

# 類型檢查
mypy src/
```

## 後續計畫

- [ ] 實作更多法規來源爬蟲
- [ ] 整合 Azure AI Search 向量搜尋
- [ ] 新增差異分析功能
- [ ] 新增合規評估報告生成
- [x] Docker 容器化
- [ ] 遷移至 Azure Functions
- [ ] CI/CD 自動化流程

## 貢獻

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳情。

## 安全

如果您發現安全漏洞，請參閱 [SECURITY.md](SECURITY.md) 了解回報方式。

## 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案
