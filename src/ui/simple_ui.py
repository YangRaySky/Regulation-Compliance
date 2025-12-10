"""
Gradio UI 元件 - 簡化版聊天介面

移除複雜的 gr.State 和 gr.JSON 以避免 JSON schema bug
"""

import gradio as gr

from .handlers import get_handler

# 使用全域變數管理會話狀態（簡化版）
_sessions = {}


def _format_structured_report(data: dict) -> str:
    """
    格式化結構化法規報告為 Markdown

    Args:
        data: Validator 輸出的結構化資料

    Returns:
        格式化的 Markdown 字串
    """
    lines = []

    # 摘要
    summary = data.get('summary', '')
    if summary:
        lines.append("## 📋 查詢結果摘要\n")
        lines.append(f"{summary}\n")

    # 相關法規列表
    regulations = data.get('verified_regulations', [])
    if regulations:
        lines.append(f"\n## 📚 相關法規 ({len(regulations)} 項)\n")
        for i, reg in enumerate(regulations, 1):
            name = reg.get('name', '未知')
            name_zh = reg.get('name_zh', '')
            if name.endswith('...'):
                name = name[:-3].rstrip()

            # 法規標題
            if name_zh and name_zh != name:
                lines.append(f"### {i}. {name}\n")
                lines.append(f"**中文名稱**: {name_zh}\n")
            else:
                lines.append(f"### {i}. {name}\n")

            # 基本資訊
            jurisdiction = reg.get('jurisdiction', '')
            reg_type = reg.get('type', '')
            url = reg.get('url', '')
            relevance = reg.get('relevance_score', 0)

            if jurisdiction:
                lines.append(f"- **適用地區**: {jurisdiction}\n")
            if reg_type:
                lines.append(f"- **法規類型**: {reg_type}\n")
            if relevance:
                lines.append(f"- **相關度**: {int(relevance * 100)}%\n")
            if url:
                lines.append(f"- **來源**: {url}\n")

            # 重點摘要
            key_points = reg.get('key_points', [])
            if key_points:
                lines.append("\n**重點摘要**:\n")
                for point in key_points:
                    lines.append(f"- {point}\n")

            # 條文節錄
            excerpts = reg.get('article_excerpts', [])
            if excerpts:
                lines.append("\n**條文節錄**:\n")
                for excerpt in excerpts:
                    article_num = excerpt.get('article_number', '')
                    title = excerpt.get('title', '')
                    content = excerpt.get('content', '')
                    relevance_note = excerpt.get('relevance', '')

                    if article_num:
                        header = f"**{article_num}**"
                        if title:
                            header += f" - {title}"
                        lines.append(f"\n{header}\n")

                    if content:
                        # 縮排顯示條文內容
                        lines.append(f"> {content}\n")

                    if relevance_note:
                        lines.append(f"*關聯說明: {relevance_note}*\n")

            # 備註
            notes = reg.get('notes', '')
            if notes:
                lines.append(f"\n📝 {notes}\n")

            lines.append("\n---\n")

    # 時間軸
    timeline = data.get('timeline', [])
    if timeline:
        lines.append("\n## 📅 法規時間軸\n")
        lines.append("| 日期 | 事件 | 相關法規 |\n")
        lines.append("|------|------|----------|\n")
        for event in timeline:
            date = event.get('date', '未知')
            event_desc = event.get('event', '')
            regulation = event.get('regulation', '')
            lines.append(f"| {date} | {event_desc} | {regulation} |\n")
        lines.append("\n")

    # 合規檢核清單
    checklist = data.get('compliance_checklist', [])
    if checklist:
        lines.append("\n## ✅ 合規檢核清單\n")
        for i, item in enumerate(checklist, 1):
            item_name = item.get('item', '')
            description = item.get('description', '')
            basis = item.get('regulation_basis', '')
            priority = item.get('priority', 'medium')
            action = item.get('action_required', '')

            # 優先級圖示
            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')

            lines.append(f"### {priority_icon} {i}. {item_name}\n")
            if description:
                lines.append(f"- **說明**: {description}\n")
            if basis:
                lines.append(f"- **法規依據**: {basis}\n")
            if action:
                lines.append(f"- **建議行動**: {action}\n")
            lines.append("\n")

    # 警告與限制
    warnings = data.get('warnings', [])
    if warnings:
        lines.append("\n## ⚠️ 注意事項\n")
        for w in warnings:
            lines.append(f"- {w}\n")

    limitations = data.get('limitations', [])
    if limitations:
        lines.append("\n## 📌 分析限制\n")
        for l in limitations:
            lines.append(f"- {l}\n")

    # 信心分數
    confidence = data.get('confidence_score', 0)
    if confidence:
        lines.append(f"\n---\n*分析信心度: {int(confidence * 100)}%*\n")

    return "".join(lines) if lines else "❌ 無法生成報告"


def create_simple_app() -> gr.Blocks:
    """
    建立簡化版 Gradio 應用程式

    Returns:
        Gradio Blocks 應用程式
    """

    with gr.Blocks(title="資安法規合規代理人系統") as app:

        # 標題區
        gr.Markdown("""
        # 🔒 資安法規合規代理人系統 (LangGraph Multi-Agent)

        智慧型法規查詢助手，使用多 Agent 協作完成查詢任務。
        """)

        # ===== 使用 Tabs 分隔功能 =====
        with gr.Tabs():
            # ===== Tab 1: 智慧查詢 =====
            with gr.Tab("🔍 智慧查詢"):
                gr.Markdown("""
                **Agent 團隊** (LangGraph):
                - 📋 **Planner**: 分析查詢意圖並制定策略
                - 🔍 **Researcher**: 使用工具執行搜尋
                - ✅ **Validator**: 驗證結果準確性

                **使用方式**：直接輸入您的問題，系統會自動確認意圖並進行搜尋。
                """)

                with gr.Row():
                    # 左側：聊天區
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="對話",
                            height=500,
                        )

                        with gr.Row():
                            msg_input = gr.Textbox(
                                label="輸入訊息",
                                placeholder="請輸入您想查詢的法規，例如：日本的資訊安全法規",
                                lines=2,
                                scale=4,
                            )
                            send_btn = gr.Button("發送", variant="primary", scale=1)

                        with gr.Row():
                            clear_btn = gr.Button("清除對話")

                        # 快捷查詢按鈕
                        gr.Markdown("### 快捷查詢範例")
                        with gr.Row():
                            quick1 = gr.Button("🇹🇼 台灣個資法", size="sm")
                            quick2 = gr.Button("🇯🇵 日本資安法規", size="sm")
                            quick3 = gr.Button("🇪🇺 GDPR", size="sm")
                            quick4 = gr.Button("🇺🇸 NIST框架", size="sm")

                    # 右側：資訊面板
                    with gr.Column(scale=1):
                        gr.Markdown("### 系統狀態")
                        status_box = gr.Textbox(
                            label="處理狀態",
                            lines=8,
                            interactive=False,
                        )

                        gr.Markdown("### 查詢結果")
                        result_box = gr.Textbox(
                            label="詳細資料",
                            lines=8,
                            interactive=False,
                        )

                        # ===== 快取管理區塊 =====
                        gr.Markdown("### 📦 快取管理")
                        skip_cache_checkbox = gr.Checkbox(
                            label="強制重新查詢（忽略快取）",
                            value=False,
                        )
                        cache_list = gr.Dataframe(
                            headers=["查詢內容", "時間（分鐘前）"],
                            datatype=["str", "number"],
                            label="快取列表",
                            interactive=False,
                            row_count=5,
                        )
                        with gr.Row():
                            refresh_cache_btn = gr.Button("🔄 重新整理", size="sm")
                            clear_cache_btn = gr.Button("🗑️ 清空全部", size="sm", variant="stop")

                        # ===== 匯出功能區塊 =====
                        gr.Markdown("### 📤 匯出報告")
                        export_format = gr.Dropdown(
                            choices=[
                                ("Markdown (.md)", "markdown"),
                                ("JSON (.json)", "json"),
                                ("PDF (.pdf)", "pdf"),
                                ("Word (.docx)", "docx"),
                                ("Excel (.xlsx)", "xlsx"),
                            ],
                            value="markdown",
                            label="匯出格式",
                        )
                        export_btn = gr.Button("📥 匯出報告", variant="primary")
                        export_file = gr.File(label="下載檔案")

                        # ===== 歷史記錄區塊 =====
                        gr.Markdown("### 📜 歷史記錄")
                        history_list = gr.Dataframe(
                            headers=["ID", "查詢內容", "法規數", "時間(分鐘前)"],
                            datatype=["str", "str", "number", "number"],
                            label="歷史記錄（點擊列自動填入 ID）",
                            interactive=False,
                            row_count=5,
                            column_widths=["80px", "auto", "60px", "80px"],
                        )
                        with gr.Row():
                            history_id_input = gr.Textbox(
                                label="輸入 ID 載入",
                                placeholder="輸入歷史 ID",
                                scale=2,
                            )
                            load_history_btn = gr.Button("📂 載入", size="sm", scale=1)
                        with gr.Row():
                            refresh_history_btn = gr.Button("🔄 重新整理", size="sm")
                            clear_history_btn = gr.Button("🗑️ 清空歷史", size="sm", variant="stop")

                        gr.Markdown("""
                        ---
                        ### 功能特色

                        - **真實搜尋**：使用 Web 搜尋、爬蟲工具獲取最新法規
                        - **多 Agent 協作**：Planner → Researcher → Validator 分工合作
                        - **智慧識別**：自動識別查詢中的地區和法規類型
                        - **意圖確認**：廣泛查詢時會先確認您的具體需求
                        - **多地區支援**：台灣、日本、歐盟、美國、國際標準
                        """)

            # ===== Tab 2: 法規資料庫瀏覽 =====
            with gr.Tab("📚 法規資料庫"):
                gr.Markdown("""
                ### 法規 Baseline 資料庫

                瀏覽系統收錄的各國各產業法規。點擊法規可查看詳情與官方連結。
                """)

                with gr.Row():
                    # 篩選器
                    db_region_filter = gr.Dropdown(
                        label="地區",
                        choices=[("全部地區", "all")],
                        value="all",
                        scale=1,
                    )
                    db_country_filter = gr.Dropdown(
                        label="國家",
                        choices=[("全部國家", "all")],
                        value="all",
                        scale=1,
                    )
                    db_industry_filter = gr.Dropdown(
                        label="產業",
                        choices=[("全部產業", "all")],
                        value="all",
                        scale=1,
                    )
                    db_refresh_btn = gr.Button("🔄 重新整理", scale=1)

                # 統計資訊
                db_stats = gr.Markdown("載入中...")

                # 法規列表
                db_regulation_list = gr.Dataframe(
                    headers=["國家", "產業", "法規名稱", "類型", "適用範圍", "連結"],
                    datatype=["str", "str", "str", "str", "str", "str"],
                    label="法規清單",
                    interactive=False,
                    wrap=True,
                    row_count=15,
                )

                # 選中的法規詳情
                with gr.Accordion("📋 法規詳情", open=False):
                    db_detail_markdown = gr.Markdown("請點擊上方表格中的法規查看詳情")

                # 免責聲明
                gr.Markdown("""
                ---
                ⚠️ **免責聲明**：本資料庫內容僅供參考，不構成法律意見。法規內容可能隨時更新，請以各主管機關公告之最新版本為準。
                """)

        # ===== 法規資料庫瀏覽函數 =====
        def get_db_filters():
            """取得篩選器選項"""
            from ..database import BaselineManager
            from ..database.models import Industry, get_session
            manager = BaselineManager()

            # 地區選項
            regions = [("全部地區", "all")]
            region_set = set()
            countries = manager.get_all_countries()
            for c in countries:
                if c['region'] and c['region'] not in region_set:
                    region_set.add(c['region'])
                    regions.append((c['region'], c['region']))

            # 國家選項
            country_choices = [("全部國家", "all")]
            for c in sorted(countries, key=lambda x: x['name_zh']):
                country_choices.append((f"{c['name_zh']} ({c['code']})", c['code']))

            # 產業選項
            industry_choices = [("全部產業", "all"), ("🌐 跨產業通用", "cross_industry")]
            session = get_session()
            industries = session.query(Industry).filter(Industry.is_active == True).all()
            for ind in sorted(industries, key=lambda x: x.name_zh):
                industry_choices.append((f"{ind.name_zh}", ind.code))
            session.close()

            manager.close()
            return regions, country_choices, industry_choices

        def update_country_choices(region_filter: str):
            """根據地區更新國家選項"""
            from ..database import BaselineManager
            manager = BaselineManager()

            countries = manager.get_all_countries()
            country_choices = [("全部國家", "all")]

            for c in sorted(countries, key=lambda x: x['name_zh']):
                if region_filter == "all" or c.get('region') == region_filter:
                    country_choices.append((f"{c['name_zh']} ({c['code']})", c['code']))

            manager.close()
            return gr.Dropdown(choices=country_choices, value="all")

        # 用於儲存當前篩選後的法規列表（供詳情查詢使用）
        _current_filtered_regulations = []

        # 產業代碼對應中文名稱
        INDUSTRY_NAMES = {
            "finance_general": "金融業",
            "banking": "銀行業",
            "securities": "證券業",
            "insurance": "保險業",
            "fintech": "金融科技",
            "healthcare": "醫療",
            "pharmaceutical": "製藥",
            "medical_device": "醫療器材",
            "technology": "科技業",
            "telecom": "電信業",
            "ecommerce": "電商",
            "manufacturing": "製造業",
            "energy": "能源",
            "retail": "零售",
            "logistics": "物流",
            "education": "教育",
            "government": "政府",
        }

        def get_db_regulations_with_cache(region_filter: str = "all", country_filter: str = "all", industry_filter: str = "all"):
            """取得法規列表並快取（供詳情查詢使用）"""
            nonlocal _current_filtered_regulations
            from ..database import BaselineManager
            manager = BaselineManager()

            # 取得所有法規
            regulations = manager.get_regulations_by_query()

            # 篩選
            filtered = []
            countries_info = {c['code']: c for c in manager.get_all_countries()}

            for reg in regulations:
                # 地區篩選
                if region_filter != "all":
                    country_info = countries_info.get(reg.country_code, {})
                    if country_info.get('region') != region_filter:
                        continue

                # 國家篩選
                if country_filter != "all" and reg.country_code != country_filter:
                    continue

                # 產業篩選
                if industry_filter != "all":
                    if industry_filter == "cross_industry":
                        # 只顯示跨產業通用法規
                        if not reg.is_cross_industry:
                            continue
                    else:
                        # 檢查是否適用於該產業
                        applicable = reg.applicable_industries or [reg.industry_code]
                        if industry_filter not in applicable and not reg.is_cross_industry:
                            continue

                filtered.append(reg)

            # 快取篩選結果
            _current_filtered_regulations = filtered

            # 轉換為 Dataframe 格式
            data = []
            for reg in filtered:
                country_info = countries_info.get(reg.country_code, {})
                country_name = country_info.get('name_zh', reg.country_code)

                # 產業名稱
                industry_name = INDUSTRY_NAMES.get(reg.industry_code, reg.industry_code)

                # 適用範圍
                if reg.is_cross_industry:
                    scope = "🌐 跨產業通用"
                else:
                    applicable = reg.applicable_industries or [reg.industry_code]
                    if len(applicable) > 3:
                        scope = f"{len(applicable)} 個產業"
                    else:
                        scope = ", ".join([INDUSTRY_NAMES.get(i, i) for i in applicable[:3]])

                # 處理官方連結
                url = reg.official_url or ""
                url_display = "🔗" if url else "無"

                data.append([
                    f"{country_name}",
                    industry_name,
                    reg.name[:50] + ("..." if len(reg.name) > 50 else ""),
                    reg.regulation_type or "",
                    scope,
                    url_display,
                ])

            manager.close()

            # 統計資訊
            cross_count = sum(1 for r in filtered if r.is_cross_industry)
            stats = f"**共 {len(filtered)} 筆法規** (跨產業: {cross_count})"
            if region_filter != "all":
                stats += f" | 地區: {region_filter}"
            if country_filter != "all":
                stats += f" | 國家: {country_filter}"
            if industry_filter != "all":
                ind_name = "跨產業通用" if industry_filter == "cross_industry" else INDUSTRY_NAMES.get(industry_filter, industry_filter)
                stats += f" | 產業: {ind_name}"

            return data if data else [["", "", "（無資料）", "", "", ""]], stats

        def on_db_regulation_select(evt: gr.SelectData):
            """當使用者點擊法規列時顯示詳情"""
            from ..database import BaselineManager

            if evt.index is None:
                return "請點擊表格中的法規查看詳情"

            # 取得 row index
            idx = evt.index
            if isinstance(idx, (list, tuple)) and len(idx) >= 1:
                row_idx = idx[0]
            elif isinstance(idx, int):
                row_idx = idx
            else:
                return "無法取得選取的法規"

            # 使用快取的篩選結果
            if row_idx >= len(_current_filtered_regulations):
                return "找不到選取的法規，請重新整理列表"

            reg = _current_filtered_regulations[row_idx]

            # 取得國家資訊
            manager = BaselineManager()
            countries_info = {c['code']: c for c in manager.get_all_countries()}
            country_info = countries_info.get(reg.country_code, {})
            manager.close()

            # 適用產業
            if reg.is_cross_industry:
                scope_text = "🌐 **跨產業通用** - 適用於所有產業"
            else:
                applicable = reg.applicable_industries or [reg.industry_code]
                scope_names = [INDUSTRY_NAMES.get(i, i) for i in applicable]
                scope_text = ", ".join(scope_names)

            # 格式化詳情
            details = f"""
## {reg.name}

| 欄位 | 內容 |
|------|------|
| **英文名稱** | {reg.name_en or '無'} |
| **中文名稱** | {reg.name_zh or '無'} |
| **國家/地區** | {country_info.get('name_zh', reg.country_code)} ({reg.country_code}) |
| **主要產業** | {INDUSTRY_NAMES.get(reg.industry_code, reg.industry_code)} |
| **法規類型** | {reg.regulation_type or '未分類'} |
| **發布機關** | {reg.issuing_authority or '未知'} |
| **信心度** | {int((reg.confidence_score or 0) * 100)}% |

### 適用產業範圍
{scope_text}

### 搜尋關鍵字
{', '.join(reg.search_keywords) if reg.search_keywords else '無'}

### 官方連結
{f'🔗 **[點擊前往官方網站]({reg.official_url})**' if reg.official_url else '❌ 無官方連結'}
"""
            return details

        # ===== 快取管理函數 =====
        def get_cache_list():
            """取得快取列表"""
            from ..utils.cache import get_cache
            cache = get_cache()
            items = cache.list_all()
            # 轉換為 Dataframe 格式
            data = []
            for item in items[:10]:  # 最多顯示 10 筆
                query_preview = item['query'][:30] + '...' if len(item['query']) > 30 else item['query']
                data.append([query_preview, item['age_minutes']])
            return data if data else [["（無快取）", 0]]

        def clear_all_cache():
            """清空所有快取"""
            from ..utils.cache import get_cache
            cache = get_cache()
            count = cache.clear_all()
            # 同時清除 session 中的 last_result
            session_id = "default"
            if session_id in _sessions:
                _sessions[session_id]["last_result"] = None
            return [["（已清空）", 0]], f"✅ 已清空 {count} 筆快取", None  # 最後一個 None 清除下載連結

        # ===== 歷史記錄函數 =====
        def get_history_list():
            """取得歷史記錄列表"""
            from ..utils.history import get_history
            history = get_history()
            items = history.list_all()
            # 轉換為 Dataframe 格式
            data = []
            for item in items[:10]:  # 最多顯示 10 筆
                query_preview = item['query'][:25] + '...' if len(item['query']) > 25 else item['query']
                data.append([item['id'], query_preview, item['reg_count'], item['age_minutes']])
            return data if data else [["", "（無歷史記錄）", 0, 0]]

        def load_history_item(history_id: str, chat_history):
            """載入歷史記錄項目"""
            import json

            from ..utils.history import get_history

            if not history_id or not history_id.strip():
                return chat_history, "❌ 請輸入歷史 ID", "", get_history_list(), None

            history = get_history()
            item = history.get(history_id.strip())

            if not item:
                return chat_history, f"❌ 找不到 ID: {history_id}", "", get_history_list(), None

            # 將結果載入到 session
            session_id = "default"
            if session_id not in _sessions:
                _sessions[session_id] = {}
            _sessions[session_id]["last_result"] = item.get("result")

            # 格式化回應
            result = item.get("result", {})
            regulations_data = result.get("regulations", {})

            if isinstance(regulations_data, dict) and 'verified_regulations' in regulations_data:
                bot_response = _format_structured_report(regulations_data)
            else:
                bot_response = f"已載入歷史查詢：{item.get('query', '')}"

            # 更新聊天記錄
            if chat_history is None:
                chat_history = []
            chat_history = chat_history + [
                {"role": "user", "content": f"[載入歷史] {item.get('query', '')}"},
                {"role": "assistant", "content": bot_response},
            ]

            result_text = json.dumps(result, ensure_ascii=False, indent=2)

            return chat_history, f"✅ 已載入歷史記錄 {history_id}", result_text, get_history_list(), None

        def clear_all_history():
            """清空所有歷史記錄"""
            from ..utils.history import get_history
            history = get_history()
            count = history.clear_all()
            return [["", "（已清空）", 0, 0]], f"✅ 已清空 {count} 筆歷史記錄"

        # ===== 匯出函數 =====
        def export_report(format_choice: str):
            """匯出報告"""
            import tempfile
            from pathlib import Path

            from ..utils.export import export_result

            session_id = "default"
            if session_id not in _sessions or "last_result" not in _sessions[session_id]:
                return None, "❌ 沒有可匯出的查詢結果，請先執行查詢"

            last_result = _sessions[session_id]["last_result"]
            if not last_result or last_result.get("status") != "success":
                return None, "❌ 沒有成功的查詢結果可匯出"

            try:
                content, filename, mime = export_result(last_result, format_choice)

                # 建立暫存檔案
                temp_dir = Path(tempfile.gettempdir()) / "regulation_exports"
                temp_dir.mkdir(exist_ok=True)
                temp_file = temp_dir / filename

                if isinstance(content, bytes):
                    temp_file.write_bytes(content)
                else:
                    temp_file.write_text(content, encoding="utf-8")

                return str(temp_file), f"✅ 已生成 {filename}"

            except Exception as e:
                return None, f"❌ 匯出失敗: {str(e)}"

        # ===== 事件處理函數 =====
        def respond(message: str, chat_history, skip_cache: bool = False):
            """
            處理使用者訊息並回應 (Gradio 6.x messages 格式)
            使用 generator 實現串流輸出，即時更新 UI
            現在支援多輪對話記憶
            """
            import json

            from ..utils.conversation import get_conversation

            # 初始化會話狀態
            session_id = "default"
            if session_id not in _sessions:
                _sessions[session_id] = {
                    "pending_clarification": False,
                    "awaiting_confirmation": False,
                    "original_query": None,
                    "last_result": None,
                }

            state = _sessions[session_id]

            # 取得對話歷史管理器（保留最近 10 輪）
            conversation = get_conversation(session_id, max_turns=10)

            if chat_history is None:
                chat_history = []

            if not message.strip():
                yield chat_history, "", "", get_cache_list(), get_history_list()
                return

            # 加入使用者訊息到對話歷史
            conversation.add_user_message(message)

            # 加入使用者訊息 (messages 格式)
            chat_history = chat_history + [{"role": "user", "content": message}]

            handler = get_handler()
            status_lines = []
            bot_response = ""
            result_text = ""

            # ===== 串流輸出：立即顯示用戶訊息 =====
            yield chat_history, "⏳ 處理中...", "", get_cache_list(), get_history_list()

            try:
                # 準備查詢內容
                actual_query = message

                # 如果正在等待確認，將訊息視為確認或補充
                if state.get("awaiting_confirmation"):
                    state["awaiting_confirmation"] = False
                    state["pending_clarification"] = False
                    # 結合原始查詢和澄清回覆
                    original = state.get("original_query", "")
                    if original:
                        actual_query = f"{original}\n\n【用戶補充說明】\n{message}"
                    status_lines.append("✅ 已收到用戶回覆")
                    status_lines.append("🔍 正在根據您的需求執行搜尋...")
                    # ===== 串流輸出：顯示確認狀態 =====
                    yield chat_history, "\n".join(status_lines), "", get_cache_list(), get_history_list()

                # 準備對話歷史上下文（排除當前訊息，避免重複）
                # 取得除了最後一條（當前訊息）之外的歷史
                all_history = conversation.get_history()
                if len(all_history) > 1:
                    # 排除剛加入的當前訊息
                    previous_history = all_history[:-1]
                    formatted_history = "\n\n".join([
                        f"[{'使用者' if t.role == 'user' else '助手'}]: {t.content[:500] + '...' if len(t.content) > 500 else t.content}"
                        for t in previous_history
                    ])
                else:
                    formatted_history = ""

                # 準備上次結果摘要（用於追問）
                previous_summary = ""
                if state.get("last_result"):
                    last_result = state["last_result"]
                    regulations = last_result.get("regulations", {})
                    if isinstance(regulations, dict):
                        verified = regulations.get("verified_regulations", [])
                        if verified:
                            summary_parts = [f"找到 {len(verified)} 筆法規:"]
                            for i, reg in enumerate(verified[:5], 1):
                                name = reg.get('name', reg.get('name_zh', '未知'))
                                summary_parts.append(f"{i}. {name}")
                            previous_summary = "\n".join(summary_parts)

                # 處理查詢（傳入對話歷史）
                for status, result in handler.process_query(
                    query=actual_query,
                    jurisdiction="自動偵測",
                    skip_cache=skip_cache,
                    conversation_history=formatted_history,
                    previous_results_summary=previous_summary,
                ):
                    status_lines.append(status)

                    # ===== 串流輸出：每次狀態更新都 yield =====
                    yield chat_history, "\n".join(status_lines), result_text, get_cache_list(), get_history_list()

                    if result:
                        # 檢查 Planner 是否需要澄清
                        if result.get("status") == "needs_clarification":
                            state["pending_clarification"] = True
                            state["awaiting_confirmation"] = True
                            state["original_query"] = message  # 儲存原始查詢

                            # 構建澄清訊息
                            questions = result.get("questions", [])
                            bot_response = "📋 **需要確認您的查詢意圖**\n\n"
                            bot_response += "為了提供更精確的法規資訊，請協助回答以下問題：\n\n"
                            for i, q in enumerate(questions, 1):
                                bot_response += f"**問題 {i}**: {q}\n\n"
                            bot_response += "請在下方輸入您的回覆，或直接補充更具體的查詢內容。"

                            status_lines.append("⏸️ 等待用戶確認查詢意圖")

                            # 顯示分析結果
                            analysis = result.get("analysis", {})
                            if analysis:
                                result_text = "**Planner 分析結果**:\n"
                                result_text += json.dumps(analysis, ensure_ascii=False, indent=2)

                        else:
                            state["pending_clarification"] = False
                            state["awaiting_confirmation"] = False

                            # 儲存成功的查詢結果（供匯出使用）
                            if result.get("status") == "success":
                                state["last_result"] = result
                                # 同時儲存到歷史記錄
                                from ..utils.history import get_history
                                history = get_history()
                                history.add(actual_query, result)

                            # 檢查是否為新格式（含 summary、timeline、compliance_checklist）
                            regulations_data = result.get("regulations", {})
                            is_new_format = isinstance(regulations_data, dict) and 'verified_regulations' in regulations_data

                            if is_new_format:
                                # 新格式：結構化報告
                                bot_response = _format_structured_report(regulations_data)
                                result_text = json.dumps(result, ensure_ascii=False, indent=2)
                            else:
                                # 舊格式：簡單列表
                                regulations = regulations_data if isinstance(regulations_data, list) else []
                                if regulations:
                                    bot_response = f"✅ **找到 {len(regulations)} 筆相關資訊**\n\n"
                                    for i, reg in enumerate(regulations, 1):
                                        name = (reg.get('name') or reg.get('name_ja') or reg.get('name_zh') or
                                               reg.get('title') or '未知')
                                        if name.endswith('...'):
                                            name = name[:-3].rstrip()

                                        bot_response += f"**{i}. {name}**\n"

                                        jurisdiction = reg.get('jurisdiction')
                                        reg_type = reg.get('type')
                                        if jurisdiction and jurisdiction != '未知':
                                            bot_response += f"   - 地區: {jurisdiction}\n"
                                        if reg_type and reg_type != '未知':
                                            bot_response += f"   - 類型: {reg_type}\n"

                                        summary = reg.get('summary') or reg.get('snippet') or reg.get('note')
                                        if summary:
                                            if len(summary) > 300:
                                                summary = summary[:300] + "..."
                                            bot_response += f"   - 說明: {summary}\n"

                                        source = reg.get('official_source') or reg.get('source_url') or reg.get('url')
                                        if source:
                                            bot_response += f"   - 來源: {source}\n"

                                        bot_response += "\n"

                                    notes = result.get("notes")
                                    if notes:
                                        bot_response += f"\n📝 **備註**: {notes}"

                                    result_text = json.dumps(result, ensure_ascii=False, indent=2)
                                else:
                                    bot_response = "❌ 抱歉，未能找到符合的法規。"
                                    notes = result.get("notes")
                                    if notes:
                                        bot_response += f"\n\n📝 **說明**: {notes}"

                                    result_text = json.dumps(result, ensure_ascii=False, indent=2)

            except Exception as e:
                bot_response = f"❌ 處理過程發生錯誤：{str(e)}"
                status_lines.append(f"錯誤: {e}")
                import traceback
                status_lines.append(traceback.format_exc())
                result_text = f"錯誤詳情:\n{traceback.format_exc()}"

            # 添加 assistant 回應到對話歷史（用於多輪對話）
            conversation.add_assistant_message(bot_response)

            # 添加 assistant 回應 (messages 格式)
            chat_history = chat_history + [{"role": "assistant", "content": bot_response}]

            status_text = "\n".join(status_lines)

            # ===== 最終輸出：完整結果 =====
            yield chat_history, status_text, result_text, get_cache_list(), get_history_list()

        def clear_chat():
            """清除對話和對話歷史"""
            from ..utils.conversation import clear_conversation

            session_id = "default"
            if session_id in _sessions:
                _sessions[session_id] = {
                    "pending_clarification": False,
                    "awaiting_confirmation": False,
                    "original_query": None,
                    "last_result": None,  # 清除匯出用的結果
                }
            # 清除多輪對話歷史
            clear_conversation(session_id)
            return [], "", "", get_cache_list(), get_history_list(), None  # 最後一個 None 清除下載連結

        def set_quick_query(query: str):
            """設定快捷查詢"""
            return query

        def on_history_select(evt: gr.SelectData):
            """當使用者點擊歷史記錄列時，自動填入 ID"""
            if evt.index is not None and evt.value is not None:
                # Gradio 6.x: evt.index 可能是 (row, col) 元組、[row, col] 列表或單一整數
                # 需要從中提取 row index
                idx = evt.index
                if isinstance(idx, (list, tuple)) and len(idx) >= 1:
                    row_idx = idx[0]
                elif isinstance(idx, int):
                    row_idx = idx
                else:
                    return ""

                # 確保 row_idx 是整數
                if not isinstance(row_idx, int):
                    return ""

                history_data = get_history_list()
                if history_data and row_idx < len(history_data):
                    history_id = history_data[row_idx][0]  # 第一欄是 ID
                    if history_id and history_id not in ["（無歷史記錄）", "（已清空）", ""]:
                        return history_id
            return ""

        # ===== 事件綁定 =====
        msg_input.submit(
            respond,
            inputs=[msg_input, chatbot, skip_cache_checkbox],
            outputs=[chatbot, status_box, result_box, cache_list, history_list],
        ).then(
            lambda: "",
            None,
            msg_input,
        )

        send_btn.click(
            respond,
            inputs=[msg_input, chatbot, skip_cache_checkbox],
            outputs=[chatbot, status_box, result_box, cache_list, history_list],
        ).then(
            lambda: "",
            None,
            msg_input,
        )

        clear_btn.click(
            clear_chat,
            None,
            [chatbot, status_box, result_box, cache_list, history_list, export_file],
        )

        # 快取管理按鈕
        refresh_cache_btn.click(
            get_cache_list,
            None,
            cache_list,
        )

        clear_cache_btn.click(
            clear_all_cache,
            None,
            [cache_list, status_box, export_file],
        )

        # 匯出按鈕
        export_btn.click(
            export_report,
            inputs=[export_format],
            outputs=[export_file, status_box],
        )

        # 歷史記錄按鈕
        refresh_history_btn.click(
            get_history_list,
            None,
            history_list,
        )

        # 點擊歷史記錄列自動填入 ID
        history_list.select(
            on_history_select,
            None,
            history_id_input,
        )

        load_history_btn.click(
            load_history_item,
            inputs=[history_id_input, chatbot],
            outputs=[chatbot, status_box, result_box, history_list, export_file],
        )

        clear_history_btn.click(
            clear_all_history,
            None,
            [history_list, status_box],
        )

        # 快捷查詢按鈕
        quick1.click(
            lambda: "請查詢台灣的個人資料保護法",
            None,
            msg_input,
        )
        quick2.click(
            lambda: "請查詢日本的資訊安全相關法規",
            None,
            msg_input,
        )
        quick3.click(
            lambda: "請查詢歐盟的 GDPR 法規",
            None,
            msg_input,
        )
        quick4.click(
            lambda: "請查詢美國 NIST 資安框架",
            None,
            msg_input,
        )

        # ===== 法規資料庫瀏覽事件 =====
        # 初始化篩選器選項
        def init_db_tab():
            """初始化法規資料庫頁籤"""
            regions, countries, industries = get_db_filters()
            data, stats = get_db_regulations_with_cache()
            return (
                gr.Dropdown(choices=regions, value="all"),
                gr.Dropdown(choices=countries, value="all"),
                gr.Dropdown(choices=industries, value="all"),
                data,
                stats,
            )

        # 頁面載入時初始化
        app.load(
            init_db_tab,
            None,
            [db_region_filter, db_country_filter, db_industry_filter, db_regulation_list, db_stats],
        )

        # 重新整理按鈕
        db_refresh_btn.click(
            get_db_regulations_with_cache,
            inputs=[db_region_filter, db_country_filter, db_industry_filter],
            outputs=[db_regulation_list, db_stats],
        )

        # 地區篩選變更時更新國家選項和法規列表
        db_region_filter.change(
            update_country_choices,
            inputs=[db_region_filter],
            outputs=[db_country_filter],
        ).then(
            get_db_regulations_with_cache,
            inputs=[db_region_filter, db_country_filter, db_industry_filter],
            outputs=[db_regulation_list, db_stats],
        )

        # 國家篩選變更時更新法規列表
        db_country_filter.change(
            get_db_regulations_with_cache,
            inputs=[db_region_filter, db_country_filter, db_industry_filter],
            outputs=[db_regulation_list, db_stats],
        )

        # 產業篩選變更時更新法規列表
        db_industry_filter.change(
            get_db_regulations_with_cache,
            inputs=[db_region_filter, db_country_filter, db_industry_filter],
            outputs=[db_regulation_list, db_stats],
        )

        # 點擊法規列時顯示詳情
        db_regulation_list.select(
            on_db_regulation_select,
            None,
            db_detail_markdown,
        )

    return app


def launch_simple_app(
    server_name: str = "127.0.0.1",
    server_port: int = 7860,
    share: bool = False,
):
    """
    啟動簡化版 Web 應用程式

    Args:
        server_name: 伺服器位址
        server_port: 伺服器埠號
        share: 是否建立公開分享連結
    """
    app = create_simple_app()
    app.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        show_error=True,
    )
