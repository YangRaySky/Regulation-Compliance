# 貢獻指南

感謝您有興趣為「資安法規合規代理人系統」做出貢獻！

## 如何貢獻

### 回報問題 (Bug Reports)

1. 在提交新 Issue 之前，請先搜尋現有的 Issues 確認問題是否已被回報
2. 使用 Issue 模板提供詳細資訊：
   - 問題描述
   - 重現步驟
   - 預期行為 vs 實際行為
   - 環境資訊（Python 版本、作業系統等）

### 功能請求 (Feature Requests)

1. 在提交功能請求前，請先查看專案的 Roadmap
2. 描述您希望添加的功能及其用途
3. 如果可能，提供實現建議

### 提交程式碼 (Pull Requests)

1. Fork 本專案
2. 建立功能分支：`git checkout -b feature/your-feature-name`
3. 提交變更：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature-name`
5. 開啟 Pull Request

## 開發環境設定

```bash
# 複製專案
git clone https://github.com/yangjuihsiu/regulation-compliance-agent.git
cd regulation-compliance-agent

# 建立虛擬環境
python -m venv .venv
source .venv/bin/activate

# 安裝依賴（含開發工具）
pip install -r requirements.txt
pip install -e ".[dev]"

# 複製環境變數範例
cp .env.example .env
# 編輯 .env 填入必要設定
```

## 程式碼規範

### 風格指南

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 規範
- 使用 [Black](https://github.com/psf/black) 進行程式碼格式化
- 使用 [Ruff](https://github.com/astral-sh/ruff) 進行 Linting

```bash
# 格式化程式碼
black src/

# 檢查程式碼風格
ruff check src/

# 類型檢查
mypy src/
```

### 提交訊息規範

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修復 Bug
- `docs:` 文件更新
- `style:` 程式碼風格調整（不影響邏輯）
- `refactor:` 重構
- `test:` 測試相關
- `chore:` 維護性工作

範例：
```
feat: 新增日本法規爬蟲支援
fix: 修正快取過期判斷邏輯
docs: 更新 API 文件說明
```

## 測試

所有程式碼變更都應包含對應的測試：

```bash
# 執行所有測試
pytest tests/

# 執行特定測試檔案
pytest tests/test_cache.py

# 執行測試並產生覆蓋率報告
pytest --cov=src tests/
```

## 安全性注意事項

- **絕對不要**提交任何 API 金鑰或敏感資訊
- 使用 `.env` 檔案管理環境變數
- 如果發現安全漏洞，請參閱 [SECURITY.md](SECURITY.md)

## 授權

提交的所有貢獻將根據專案的 MIT 授權條款進行授權。
