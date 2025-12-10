"""
LangGraph Multi-Agent 團隊

使用 LangGraph 實作法規查詢的多 Agent 協作系統：
- Planner: 分析查詢並規劃搜尋策略
- Researcher: 執行搜尋和資料收集
- Validator: 驗證結果的準確性
"""

import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Callable, Generator, Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, StateGraph

from ..database import BaselineManager
from ..utils.config import load_prompt
from .tool_executor import execute_tool_call, parse_tool_results
from .tool_schemas import get_tool_schemas
from .tools import fetch_pdf_content, fetch_webpage

load_dotenv()


# ===== State Definition =====
class AgentState(TypedDict):
    """Agent 狀態定義"""
    messages: list  # 內部 Agent 通訊日誌
    query: str  # 原始查詢
    jurisdiction: str  # 目標地區
    conversation_history: str  # 多輪對話歷史（格式化字串）
    previous_results_summary: str  # 上次查詢結果摘要
    planner_analysis: dict  # Planner 分析結果
    clarification_needed: bool  # 是否需要澄清
    questions: list  # 澄清問題
    search_results: list  # 搜尋結果
    validated_results: list  # 驗證後的結果
    status: str  # 當前狀態
    error: Optional[str]  # 錯誤訊息


# ===== LLM Configuration (Thread-Safe Singleton) =====
_llm_instance: Optional[AzureChatOpenAI] = None
_llm_lock = threading.Lock()


def get_llm() -> AzureChatOpenAI:
    """
    取得 LLM 實例 (Azure OpenAI) - 線程安全單例模式

    使用 Double-Checked Locking 確保線程安全，
    同時避免每次呼叫都需要獲取鎖的效能開銷。
    """
    global _llm_instance

    # 第一次檢查（無鎖）
    if _llm_instance is not None:
        return _llm_instance

    # 獲取鎖後再次檢查
    with _llm_lock:
        if _llm_instance is not None:
            return _llm_instance

        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_deployment = os.getenv("AZURE_OPENAI_GPT5_DEPLOYMENT", "gpt-5.1")
        azure_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

        if not azure_endpoint or not azure_key:
            raise ValueError("未設定 Azure OpenAI 配置")

        # GPT-5.1: 400K context (272K input, 128K output)
        # 不支援自訂 temperature，只能使用預設值 1.0
        _llm_instance = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_key,
            azure_deployment=azure_deployment,
            api_version=azure_version,
            max_tokens=32768,  # 32K tokens 輸出，足夠容納大量法規的 JSON
        )

        return _llm_instance


def reset_llm():
    """重置 LLM 實例（用於測試或重新載入配置）"""
    global _llm_instance
    with _llm_lock:
        _llm_instance = None


# ===== Agent Nodes =====
def planner_node(state: AgentState) -> AgentState:
    """
    Planner Agent: 分析查詢意圖並制定搜尋策略
    現在支援多輪對話歷史，能理解追問類型的查詢
    """
    llm = get_llm()

    # 載入外部 prompt
    system_prompt = load_prompt("langgraph_planner")

    # 建構包含對話歷史的 user_message
    user_message_parts = []

    # 加入對話歷史（如果有的話）
    conversation_history = state.get('conversation_history', '')
    if conversation_history:
        user_message_parts.append(f"""【對話歷史】
以下是之前的對話記錄，請參考這些上下文來理解當前查詢：
{conversation_history}
""")

    # 加入上次結果摘要（如果有的話）
    previous_results = state.get('previous_results_summary', '')
    if previous_results:
        user_message_parts.append(f"""【上次查詢結果摘要】
{previous_results}
""")

    # 當前查詢
    user_message_parts.append(f"""【當前查詢】
使用者查詢: {state['query']}
指定地區: {state['jurisdiction']}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

請分析這個查詢並提供規劃。

**注意**：
1. 如果這是追問類型的查詢（如「還有其他嗎？」「請詳細說明第一個」），請根據對話歷史理解用戶真正想要的資訊
2. 對於追問，判斷是否需要新搜尋，還是可以基於之前的結果進行補充
3. 如果無法從歷史中判斷用戶意圖，請設定 clarification_needed: true""")

    user_message = "\n".join(user_message_parts)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content

        # 解析 JSON
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
            analysis = json.loads(json_str)
        else:
            analysis = json.loads(content)

        # 更新狀態
        state["planner_analysis"] = analysis
        state["clarification_needed"] = analysis.get("clarification_needed", False)
        state["questions"] = analysis.get("questions", [])
        state["messages"].append(AIMessage(content=f"Planner 分析: {json.dumps(analysis, ensure_ascii=False)}"))

        if state["clarification_needed"]:
            state["status"] = "needs_clarification"
        else:
            state["status"] = "ready_to_search"

    except Exception as e:
        state["error"] = f"Planner 錯誤: {str(e)}"
        state["status"] = "error"

    return state


def _get_mandatory_keywords_from_db(region: str, industry: str = None, topic: str = None) -> list[dict]:
    """
    從資料庫取得必搜關鍵字清單

    Args:
        region: 地區名稱（中文）
        industry: 產業別
        topic: 主題

    Returns:
        必搜關鍵字清單
    """
    # 地區名稱對應到國家代碼
    REGION_TO_CODE = {
        "台灣": "TW", "日本": "JP", "韓國": "KR", "中國": "CN",
        "香港": "HK", "新加坡": "SG", "馬來西亞": "MY", "泰國": "TH",
        "印尼": "ID", "越南": "VN", "菲律賓": "PH", "印度": "IN",
        "阿聯酋": "AE", "沙烏地阿拉伯": "SA", "以色列": "IL", "土耳其": "TR",
        "歐盟": "EU", "英國": "GB", "德國": "DE", "法國": "FR",
        "義大利": "IT", "西班牙": "ES", "荷蘭": "NL", "瑞士": "CH",
        "瑞典": "SE", "波蘭": "PL", "俄羅斯": "RU",
        "美國": "US", "加拿大": "CA", "墨西哥": "MX",
        "巴西": "BR", "阿根廷": "AR", "智利": "CL", "哥倫比亞": "CO",
        "澳洲": "AU", "紐西蘭": "NZ",
        "南非": "ZA", "奈及利亞": "NG", "肯亞": "KE", "埃及": "EG",
    }

    # 產業名稱對應到代碼
    INDUSTRY_TO_CODE = {
        "金融業": "finance_general", "金融": "finance_general",
        "銀行業": "banking", "銀行": "banking",
        "證券業": "securities", "證券": "securities",
        "保險業": "insurance", "保險": "insurance",
        "醫療業": "healthcare", "醫療": "healthcare",
        "科技業": "technology", "科技": "technology",
        "電信業": "telecom", "電信": "telecom",
    }

    # 主題對應到代碼
    TOPIC_TO_CODE = {
        "資安": "cybersecurity", "資訊安全": "cybersecurity", "網路安全": "cybersecurity",
        "個資": "privacy", "個人資料": "privacy", "隱私": "privacy",
        "反洗錢": "aml", "洗錢防制": "aml",
    }

    country_code = REGION_TO_CODE.get(region)
    if not country_code:
        return []

    industry_code = INDUSTRY_TO_CODE.get(industry) if industry else None
    topic_code = TOPIC_TO_CODE.get(topic) if topic else None

    try:
        manager = BaselineManager()
        keywords = manager.get_search_keywords(
            country_code=country_code,
            industry_code=industry_code,
            topic_code=topic_code,
        )
        manager.close()
        return keywords
    except Exception as e:
        print(f"[Researcher] 從資料庫取得必搜清單失敗: {e}")
        return []


def researcher_node(state: AgentState) -> AgentState:
    """
    Researcher Agent: 自主搜尋執行

    根據 Planner 的 understood 資訊，自主制定並執行搜尋策略。
    穩定性來自資料庫中的「必搜清單」+ Prompt 指導。
    """
    if state.get("status") != "ready_to_search":
        return state

    llm = get_llm()
    planner_analysis = state.get("planner_analysis", {})
    understood = planner_analysis.get("understood", {})
    findings = []

    # 從 understood 提取查詢資訊
    region = understood.get("region", state.get("jurisdiction", "未知"))
    topic = understood.get("topic", "未知")
    industry = understood.get("industry", "未知")

    # ===== 綁定工具到 LLM =====
    tool_schemas = get_tool_schemas()
    llm_with_tools = llm.bind_tools(tool_schemas)

    # 載入外部 prompt
    system_prompt = load_prompt("langgraph_researcher")

    # 從 understood 提取其他查詢資訊
    is_follow_up = understood.get("is_follow_up", False)
    time_requirement = understood.get("time_requirement", "none")

    # ===== 從資料庫取得必搜關鍵字 =====
    mandatory_keywords = _get_mandatory_keywords_from_db(region, industry, topic)
    mandatory_keywords_text = ""
    if mandatory_keywords:
        print(f"[Researcher] 從資料庫載入 {len(mandatory_keywords)} 個必搜關鍵字")
        keyword_lines = []
        for kw in mandatory_keywords:
            keyword_lines.append(f"  - 「{kw['keyword']}」→ {kw['regulation_name']}")
        mandatory_keywords_text = f"""

**必搜關鍵字清單**（來自資料庫，請優先搜尋）：
{chr(10).join(keyword_lines)}
"""

    user_message = f"""
**查詢資訊**：
- 原始查詢: {state['query']}
- 地區: {region}
- 產業: {industry}
- 主題: {topic}
- 是否為追問: {is_follow_up}
- 時間限制: {time_requirement}
{mandatory_keywords_text}
**你的任務**：根據以上資訊，制定並執行搜尋策略。

請按照 Prompt 中的指南：
1. **優先搜尋上方的必搜關鍵字**（如果有的話）
2. 識別所有相關子領域
3. 為每個子領域產生搜尋關鍵字
4. 執行至少 8-12 次搜尋
5. 確保使用當地語言和英文關鍵字
6. 完成後回覆「搜尋完成」

**重要**: 不要太快結束！確保覆蓋所有可能相關的子領域。"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    # ===== LLM 自主搜尋迴圈 =====
    MAX_SEARCH_ITERATIONS = 15  # 最多 15 輪搜尋（緩解風險：增加搜尋機會）
    total_tool_count = 0

    print(f"[Researcher] 開始自主搜尋（地區: {region}, 產業: {industry}, 主題: {topic}）...")

    for iteration in range(MAX_SEARCH_ITERATIONS):
        try:
            response = llm_with_tools.invoke(messages)

            # 檢查是否有 tool_calls
            if not response.tool_calls:
                # LLM 認為搜尋完成，沒有更多工具調用
                print(f"[Researcher] LLM 決定結束搜尋（迭代 {iteration + 1}，共 {total_tool_count} 次工具調用）")
                break

            # 處理每個 tool call
            messages.append(response)  # 加入 AI 的回應（包含 tool_calls）

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                total_tool_count += 1

                args_str = json.dumps(tool_args, ensure_ascii=False)[:60]
                print(f"[Researcher] 搜尋 {total_tool_count}: {tool_name}({args_str}...)")

                # 執行工具
                result = execute_tool_call(tool_call)

                # 解析結果並加入 findings
                parsed_results = parse_tool_results(result["content"])
                findings.extend(parsed_results)

                # 將工具結果加入對話歷史
                messages.append(ToolMessage(
                    content=result["content"],
                    tool_call_id=tool_call["id"],
                    name=tool_name
                ))

        except Exception as e:
            print(f"[Researcher] 迭代 {iteration + 1} 發生錯誤: {str(e)}")
            break

    print(f"[Researcher] 搜尋完成：共 {total_tool_count} 次工具調用，找到 {len(findings)} 筆結果")

    # ===== 去重邏輯 =====
    seen_urls = set()
    unique_findings = []
    for item in findings:
        url = item.get('url') or item.get('href') or item.get('source_url')
        if url:
            if url not in seen_urls:
                seen_urls.add(url)
                unique_findings.append(item)
        else:
            unique_findings.append(item)

    original_count = len(findings)
    deduplicated_count = len(unique_findings)

    # ===== 並行原文抓取 =====
    TOP_N_TO_FETCH = 50       # 極限模式：抓取更多原文（從 30 提升到 50）
    MAX_CONTENT_CHARS = 10000  # 增加原文長度以捕捉更多法規名稱（從 8000 提升到 10000）
    MAX_WORKERS = 10          # 增加並行線程（從 8 提升到 10）

    def fetch_single_content(item: dict) -> dict:
        """抓取單一項目的原文內容"""
        url = item.get('url') or item.get('href') or item.get('source_url')
        if not url:
            item['full_content'] = None
            item['content_fetched'] = False
            item['fetch_error'] = '無 URL'
            return item

        try:
            is_pdf = (
                url.lower().endswith('.pdf') or
                'pdf' in url.lower() or
                item.get('content_type', '').lower() == 'pdf'
            )

            if is_pdf:
                content_result = fetch_pdf_content(url=url, max_pages=10, max_chars=MAX_CONTENT_CHARS)
            else:
                content_result = fetch_webpage(url=url, extract_text=True)

            content_data = json.loads(content_result) if isinstance(content_result, str) else content_result
            if content_data.get('status') == 'success':
                full_content = content_data.get('content', '')
                if len(full_content) > MAX_CONTENT_CHARS:
                    full_content = full_content[:MAX_CONTENT_CHARS] + '\n... (內容已截斷)'
                item['full_content'] = full_content
                item['content_fetched'] = True
                item['content_type'] = 'pdf' if is_pdf else 'webpage'
            else:
                item['full_content'] = None
                item['content_fetched'] = False
                item['fetch_error'] = content_data.get('error', '抓取失敗')

        except Exception as e:
            item['full_content'] = None
            item['content_fetched'] = False
            item['fetch_error'] = str(e)

        return item

    items_to_fetch = unique_findings[:TOP_N_TO_FETCH]
    items_no_fetch = unique_findings[TOP_N_TO_FETCH:]

    for item in items_no_fetch:
        item['full_content'] = None
        item['content_fetched'] = False

    print(f"[Researcher] 開始並行抓取 {len(items_to_fetch)} 筆原文...")
    fetched_items = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_item = {
            executor.submit(fetch_single_content, item.copy()): idx
            for idx, item in enumerate(items_to_fetch)
        }

        for future in as_completed(future_to_item):
            try:
                result_item = future.result(timeout=60)
                fetched_items.append(result_item)
            except Exception as e:
                idx = future_to_item[future]
                item = items_to_fetch[idx].copy()
                item['full_content'] = None
                item['content_fetched'] = False
                item['fetch_error'] = f'抓取超時: {str(e)}'
                fetched_items.append(item)

    enriched_findings = fetched_items + items_no_fetch

    fetch_count = sum(1 for item in fetched_items if item.get('content_fetched'))
    pdf_count = sum(1 for item in fetched_items if item.get('content_type') == 'pdf')
    webpage_count = sum(1 for item in fetched_items if item.get('content_type') == 'webpage')

    print(f"[Researcher] 並行抓取完成：成功 {fetch_count}/{len(items_to_fetch)}")

    # ===== 顯示失敗原因統計 =====
    failed_items = [item for item in fetched_items if not item.get('content_fetched')]
    if failed_items:
        error_counts = {}
        for item in failed_items:
            error = item.get('fetch_error', '未知錯誤')
            # 簡化錯誤訊息（移除過長的 URL 或詳細資訊）
            if len(error) > 80:
                error = error[:77] + '...'
            error_counts[error] = error_counts.get(error, 0) + 1

        print(f"[Researcher] 抓取失敗原因統計 ({len(failed_items)} 筆):")
        # 按數量排序，顯示前 5 種錯誤
        for error, count in sorted(error_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"   - {error}: {count} 筆")

    state["search_results"] = enriched_findings
    state["status"] = "ready_to_validate"
    state["messages"].append(AIMessage(
        content=f"Researcher 自主搜尋調用 {total_tool_count} 次工具，"
                f"找到 {original_count} 筆結果，去重後 {deduplicated_count} 筆，"
                f"抓取 {fetch_count} 筆原文（PDF: {pdf_count}, 網頁: {webpage_count}）"
    ))

    return state


def validator_node(state: AgentState) -> AgentState:
    """
    Validator Agent: 驗證搜尋結果並生成結構化報告
    """
    if state.get("status") != "ready_to_validate":
        return state

    llm = get_llm()

    # 取得原始查詢資訊
    original_query = state.get("query", "")
    jurisdiction = state.get("jurisdiction", "自動偵測")

    # 載入外部 prompt
    system_prompt = load_prompt("langgraph_validator")

    # ===== 動態調整：根據原文長度自動調整數量 =====
    # GPT-5.1: 400K context (272K input, 128K output)
    # 中文約 1.5-2 token/字元，設定 150,000 字元約 225K-300K tokens
    TARGET_TOTAL_CHARS = 150000
    MAX_CONTENT_LENGTH = 2000     # 每筆原文 2000 字（充分捕捉法規內容）

    search_results = state.get('search_results', [])

    # 優先處理有原文的結果
    results_with_content = [r for r in search_results if r.get('content_fetched')]
    results_without_content = [r for r in search_results if not r.get('content_fetched')]

    # ===== 動態精簡：確保總字元數不超過限制 =====
    trimmed_results = []
    total_chars = 0

    # Phase 1: 優先加入有原文的結果
    for r in results_with_content:
        trimmed = {
            'title': r.get('title') or r.get('name') or '未知',
            'url': r.get('url') or r.get('href') or '',
            'snippet': (r.get('snippet') or r.get('body') or '')[:300],  # 限制 snippet 長度
            'content_type': r.get('content_type', 'unknown'),
        }
        # 截斷 full_content
        full_content = r.get('full_content', '')
        if full_content and len(full_content) > MAX_CONTENT_LENGTH:
            trimmed['full_content'] = full_content[:MAX_CONTENT_LENGTH] + '\n... (內容已截斷)'
        else:
            trimmed['full_content'] = full_content or ''

        # 計算此筆資料的估計字元數
        item_chars = len(json.dumps(trimmed, ensure_ascii=False))

        # 檢查是否超出限制
        if total_chars + item_chars > TARGET_TOTAL_CHARS:
            print(f"[Validator] 達到字元限制，停止於 {len(trimmed_results)} 筆有原文結果")
            break

        trimmed_results.append(trimmed)
        total_chars += item_chars

    # Phase 2: 如果還有空間，加入無原文的結果（較小的資料量）
    for r in results_without_content:
        trimmed = {
            'title': r.get('title') or r.get('name') or '未知',
            'url': r.get('url') or r.get('href') or '',
            'snippet': (r.get('snippet') or r.get('body') or '')[:200],
            'full_content': None,
        }

        item_chars = len(json.dumps(trimmed, ensure_ascii=False))

        if total_chars + item_chars > TARGET_TOTAL_CHARS:
            break

        trimmed_results.append(trimmed)
        total_chars += item_chars

    print(f"[Validator] 精簡後：{len(trimmed_results)} 筆，總計約 {total_chars:,} 字元")

    user_message = f"""
**原始查詢**: {original_query}
**目標地區**: {jurisdiction}

**搜尋結果統計**:
- 總結果數: {len(search_results)}
- 成功抓取原文: {len(results_with_content)} 筆
- 本次驗證: {len(trimmed_results)} 筆（已精簡）

**搜尋結果（已精簡）**:
{json.dumps(trimmed_results, ensure_ascii=False, indent=2)}

請根據以上資料：
1. 過濾不相關的結果
2. 從有原文的結果中提取重要條文
3. 整理時間軸
4. 生成合規檢核清單
5. 提供整體摘要

**重要**：請確保輸出為有效的 JSON 格式。"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    # ===== 增加重試機制 =====
    MAX_RETRIES = 3
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = llm.invoke(messages)
            content = response.content

            # ===== 診斷：檢測空回應 =====
            if not content or not content.strip():
                print(f"[Validator] 警告：LLM 返回空內容 (attempt {attempt + 1})")
                raise ValueError("LLM 返回空內容，可能是輸入過長或模型限制")

            print(f"[Validator] LLM 回應長度: {len(content)} 字元 (attempt {attempt + 1})")

            # 解析 JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
                validation = json.loads(json_str)
            elif "```" in content:
                # 嘗試提取任何 code block
                json_str = content.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                validation = json.loads(json_str)
            else:
                validation = json.loads(content)

            # 驗證必要欄位存在
            if 'verified_regulations' not in validation:
                validation['verified_regulations'] = []
            if 'timeline' not in validation:
                validation['timeline'] = []
            if 'compliance_checklist' not in validation:
                validation['compliance_checklist'] = []

            # 確保免責聲明存在
            if 'disclaimer' not in validation:
                validation['disclaimer'] = {
                    "zh": "本查詢結果僅供參考，不構成法律意見。法規內容可能隨時更新，"
                          "請以各主管機關公告之最新版本為準。使用者應自行諮詢專業法律人員以確認適用性。",
                    "en": "This query result is for reference only and does not constitute legal advice. "
                          "Regulatory content may be updated at any time. Please refer to the latest version "
                          "published by the relevant authorities. Users should consult qualified legal "
                          "professionals to confirm applicability."
                }

            # 成功：將完整的驗證結果存入 state
            state["validated_results"] = validation
            state["status"] = "completed"
            state["messages"].append(AIMessage(
                content=f"Validator 驗證完成: {validation.get('validation_result', 'unknown')}，"
                        f"識別 {len(validation.get('verified_regulations', []))} 項相關法規，"
                        f"生成 {len(validation.get('compliance_checklist', []))} 項檢核項目"
            ))
            return state

        except json.JSONDecodeError as e:
            last_error = e
            print(f"[Validator] JSON 解析失敗: {e} (attempt {attempt + 1})")
            # JSON 解析失敗，如果還有重試次數，添加提示後重試
            if attempt < MAX_RETRIES - 1:
                messages.append(AIMessage(content=content if content else ""))
                messages.append(HumanMessage(
                    content="上述回應無法解析為 JSON。請重新輸出，確保是有效的 JSON 格式（以 ```json 開頭，``` 結尾）。"
                ))
            continue

        except ValueError as e:
            # 空回應錯誤，重試
            last_error = e
            print(f"[Validator] ValueError: {e} (attempt {attempt + 1})")
            if attempt < MAX_RETRIES - 1:
                continue
            break

        except Exception as e:
            last_error = e
            print(f"[Validator] 未知錯誤: {type(e).__name__}: {e}")
            break

    # 所有重試都失敗，建構基本結構
    state["validated_results"] = {
        "validation_result": "error",
        "summary": f"驗證過程發生錯誤: {str(last_error)}",
        "verified_regulations": trimmed_results,  # 使用精簡後的結果
        "timeline": [],
        "compliance_checklist": [],
        "warnings": [f"驗證錯誤: {str(last_error)}"],
        "limitations": ["無法完成完整驗證，已返回原始搜尋結果"],
        "confidence_score": 0.3,
        "disclaimer": {
            "zh": "本查詢結果僅供參考，不構成法律意見。法規內容可能隨時更新，"
                  "請以各主管機關公告之最新版本為準。使用者應自行諮詢專業法律人員以確認適用性。",
            "en": "This query result is for reference only and does not constitute legal advice. "
                  "Regulatory content may be updated at any time. Please refer to the latest version "
                  "published by the relevant authorities. Users should consult qualified legal "
                  "professionals to confirm applicability."
        }
    }
    state["status"] = "completed"
    state["messages"].append(AIMessage(content=f"Validator 警告: {str(last_error)}"))

    return state


# ===== Conditional Edge =====
def should_continue(state: AgentState) -> Literal["researcher", "end"]:
    """決定下一步：繼續搜尋或結束"""
    if state.get("clarification_needed"):
        return "end"
    if state.get("error"):
        return "end"
    if state.get("status") == "ready_to_search":
        return "researcher"
    return "end"


# ===== Build Graph =====
def create_regulation_graph():
    """創建法規查詢 workflow graph"""
    workflow = StateGraph(AgentState)

    # 添加 nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("validator", validator_node)

    # 設定流程
    workflow.set_entry_point("planner")
    workflow.add_conditional_edges(
        "planner",
        should_continue,
        {
            "researcher": "researcher",
            "end": END,
        }
    )
    workflow.add_edge("researcher", "validator")
    workflow.add_edge("validator", END)

    return workflow.compile()


# ===== Main Query Handler =====
class RegulationAgentTeam:
    """
    法規查詢 Agent 團隊 (LangGraph 版本)
    """

    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        初始化 Agent 團隊

        Args:
            status_callback: 狀態更新回調函數
        """
        self.status_callback = status_callback or (lambda x: None)
        self.graph = create_regulation_graph()

        # 初始化快取
        from ..utils.cache import get_cache
        self.cache = get_cache()

        # 進度追蹤
        self._progress_messages = []

        self._report_status("LangGraph Agent 團隊初始化完成")

    def get_progress_messages(self) -> list:
        """取得並清空進度訊息"""
        msgs = self._progress_messages.copy()
        self._progress_messages.clear()
        return msgs

    def add_progress(self, message: str):
        """新增進度訊息"""
        self._progress_messages.append(message)

    def _report_status(self, message: str):
        """報告狀態"""
        self.status_callback(message)

    def process_query(
        self,
        query: str,
        jurisdiction: str = "自動偵測",
        skip_cache: bool = False,
        conversation_history: str = "",
        previous_results_summary: str = "",
    ) -> Generator[tuple[str, Optional[dict]], None, None]:
        """
        處理法規查詢

        Args:
            query: 使用者查詢
            jurisdiction: 目標地區
            skip_cache: 是否跳過快取（強制重新查詢）
            conversation_history: 格式化的對話歷史（多輪對話支援）
            previous_results_summary: 上次查詢結果摘要（用於追問）

        Yields:
            (狀態訊息, 結果資料)
        """
        yield ("🚀 啟動 LangGraph Agent 團隊...", None)

        # ===== 提取原始查詢（用於快取 key）=====
        # 如果查詢包含「用戶補充說明」，只使用第一部分作為快取 key
        cache_key_query = query.split("\n\n【用戶補充說明】")[0].strip()

        # ===== 檢查快取 =====
        if not skip_cache:
            cached_result = self.cache.get(cache_key_query, jurisdiction)
            if cached_result:
                print("[Cache] 快取命中，直接返回結果")
                yield ("📦 從快取載入結果...", None)
                cached_result['from_cache'] = True
                yield ("🎉 查詢完成（快取）!", cached_result)
                return

        # 初始化狀態（含對話歷史）
        initial_state: AgentState = {
            "messages": [],
            "query": query,
            "jurisdiction": jurisdiction,
            "conversation_history": conversation_history,
            "previous_results_summary": previous_results_summary,
            "planner_analysis": {},
            "clarification_needed": False,
            "questions": [],
            "search_results": [],
            "validated_results": [],
            "status": "starting",
            "error": None,
        }

        try:
            # ===== 使用 stream() 取代 invoke() 以獲取即時進度 =====
            final_state = None
            current_node = None

            # 預先顯示 Planner 進度（因為 stream() 在 node 完成後才返回）
            yield ("📋 Planner 正在分析查詢意圖...", None)
            yield ("   ├─ 識別目標地區與法規類型...", None)
            yield ("   └─ 規劃多關鍵字搜尋策略...", None)

            for event in self.graph.stream(initial_state):
                # event 格式: {node_name: state}
                for node_name, state in event.items():
                    if node_name != current_node:
                        # 在進入下一個 node 前顯示進度
                        if current_node == "planner" and node_name == "researcher":
                            # Planner 完成，顯示分析結果摘要
                            plan = state.get("planner_analysis", {})
                            search_plan = plan.get("search_plan", [])
                            understood = plan.get("understood", {})
                            region = understood.get("region", "未知")
                            topic = understood.get("topic", "未知")
                            yield (f"   ✓ 分析完成：{region} - {topic}", None)

                            # 顯示 Researcher 進度
                            yield ("🔍 Researcher 正在執行搜尋...", None)
                            if search_plan:
                                yield (f"   ├─ 執行 {len(search_plan)} 個多關鍵字搜尋...", None)
                            yield ("   ├─ 並行抓取網頁原文（最多 15 筆）...", None)
                            yield ("   └─ 執行去重與資料清洗...", None)

                        elif current_node == "researcher" and node_name == "validator":
                            # Researcher 完成，顯示結果摘要
                            search_results = state.get("search_results", [])
                            fetched_count = sum(1 for r in search_results if r.get("content_fetched"))
                            yield (f"   ✓ 搜尋完成：找到 {len(search_results)} 筆（抓取 {fetched_count} 篇原文）", None)

                            # 顯示 Validator 進度
                            yield ("✅ Validator 正在驗證結果...", None)
                            yield ("   ├─ 篩選相關法規...", None)
                            yield ("   ├─ 提取重要條文...", None)
                            yield ("   └─ 生成合規檢核清單...", None)

                        current_node = node_name

                    final_state = state

            # Validator 完成摘要
            if final_state and not final_state.get("clarification_needed"):
                validated = final_state.get("validated_results", {})
                if isinstance(validated, dict):
                    reg_count = len(validated.get("verified_regulations", []))
                    checklist_count = len(validated.get("compliance_checklist", []))
                    yield (f"   ✓ 驗證完成：{reg_count} 項法規、{checklist_count} 項檢核清單", None)

            # 檢查是否需要澄清
            if final_state and final_state.get("clarification_needed"):
                yield ("⏸️ 需要澄清查詢意圖", {
                    "status": "needs_clarification",
                    "query": query,
                    "questions": final_state.get("questions", []),
                    "analysis": final_state.get("planner_analysis", {}),
                    "timestamp": datetime.now().isoformat(),
                })
                return

            if not final_state:
                raise ValueError("Graph 執行未返回結果")

            # 構建最終結果
            result = {
                "status": "success",
                "query": query,
                "original_query": cache_key_query,  # 儲存原始查詢（不含補充說明）
                "model_used": "LangGraph Multi-Agent Team",
                "regulations": final_state.get("validated_results", []),
                "notes": "查詢完成",
                "timestamp": datetime.now().isoformat(),
                "from_cache": False,
            }

            # ===== 儲存到快取（使用原始查詢作為 key）=====
            cache_id = self.cache.set(cache_key_query, jurisdiction, result)
            print(f"[Cache] 結果已儲存，key: '{cache_key_query[:30]}...', ID: {cache_id}")

            yield ("🎉 查詢完成!", result)

        except Exception as e:
            yield (f"❌ 處理過程發生錯誤: {str(e)}", {
                "status": "error",
                "error": str(e),
            })


# ===== 便捷函數 =====
_team_instance: Optional[RegulationAgentTeam] = None


def get_agent_team(status_callback: Optional[Callable[[str], None]] = None) -> RegulationAgentTeam:
    """取得全域 Agent 團隊實例"""
    global _team_instance
    if _team_instance is None:
        _team_instance = RegulationAgentTeam(status_callback)
    return _team_instance


def reset_agent_team():
    """重置 Agent 團隊"""
    global _team_instance
    _team_instance = None
