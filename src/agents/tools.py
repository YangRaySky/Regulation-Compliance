"""
Agent 工具函數

提供給 LangGraph Agents 使用的工具，包括：
- Web 搜尋（支援 Google Custom Search API 或 DuckDuckGo）
- 法規爬蟲（台灣、日本、歐盟）
- 網頁/PDF 內容擷取
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

import httpx
import yaml
from dotenv import load_dotenv

load_dotenv()


# ===== 地區設定載入 =====

def _load_region_config() -> dict[str, dict[str, Any]]:
    """
    從 YAML 檔案載入地區搜尋設定

    Returns:
        地區設定字典，key 為地區名稱
    """
    # 嘗試多個可能的路徑
    possible_paths = [
        Path("config/regions.yaml"),
        Path(__file__).parent.parent.parent / "config" / "regions.yaml",
    ]

    for path in possible_paths:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}

    # 找不到設定檔時回傳空字典（不中斷程式）
    print("警告: 找不到 config/regions.yaml，地區搜尋設定將為空")
    return {}


# 載入地區設定（模組層級，只載入一次）
REGION_CONFIG = _load_region_config()


# ===== 輔助函數 =====

def _json_response(
    status: str,
    data: dict[str, Any] | None = None,
    error: str | None = None,
) -> str:
    """統一的 JSON 回應格式"""
    response = {"status": status}
    if data:
        response.update(data)
    if error:
        response["error"] = error
    return json.dumps(response, ensure_ascii=False, indent=2)


import random

# 常見瀏覽器 User-Agent 列表（2024 年版本）
_USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


def _get_http_client(timeout: int = 30) -> httpx.Client:
    """建立統一設定的 HTTP 客戶端（含反反爬蟲 Headers）"""
    # 隨機選擇 User-Agent
    user_agent = random.choice(_USER_AGENTS)

    # 模擬真實瀏覽器的 Headers
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,ja;q=0.6",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    return httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        headers=headers,
    )


def _validate_url(url: str) -> tuple[bool, str]:
    """
    驗證 URL 安全性，防止 SSRF 攻擊

    Args:
        url: 要驗證的 URL

    Returns:
        (是否有效, 錯誤訊息)
    """
    import ipaddress
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)

        # 檢查 1：只允許 http/https 協議
        if parsed.scheme not in ('http', 'https'):
            return False, f"不支援的協議: {parsed.scheme}，僅支援 http/https"

        # 檢查 2：必須有主機名稱
        if not parsed.hostname:
            return False, "URL 缺少主機名稱"

        hostname = parsed.hostname.lower()

        # 檢查 3：禁止本地網址（防止 SSRF）
        blocked_hosts = ('localhost', '127.0.0.1', '0.0.0.0', '::1')
        if hostname in blocked_hosts:
            return False, "不允許存取本地網址"

        # 檢查 4：禁止內網 IP 範圍
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private:
                return False, "不允許存取內部網路位址（私有 IP）"
            if ip.is_loopback:
                return False, "不允許存取迴環位址"
            if ip.is_reserved:
                return False, "不允許存取保留位址"
            if ip.is_link_local:
                return False, "不允許存取鏈路本地位址"
        except ValueError:
            # 不是 IP 格式，是域名，這是允許的
            pass

        return True, ""

    except Exception as e:
        return False, f"URL 解析失敗: {str(e)}"


def _match_laws_by_keywords(
    query: str,
    laws_db: dict[str, dict],
    jurisdiction: str,
) -> list[dict]:
    """
    通用的關鍵字匹配法規函數

    Args:
        query: 搜尋關鍵字
        laws_db: 法規資料庫，格式為 {法規名: {info...}}
        jurisdiction: 管轄區域（台灣、日本、歐盟）

    Returns:
        匹配的法規列表
    """
    matched = []
    query_lower = query.lower()

    for law_name, info in laws_db.items():
        keywords = info.get("keywords", [])
        name_zh = info.get("name_zh", "")

        # 檢查關鍵字匹配
        keyword_match = any(kw in query_lower or kw in query for kw in keywords)
        # 檢查法規名稱匹配
        name_match = law_name.lower() in query_lower or name_zh in query

        if keyword_match or name_match:
            result = {
                "title": law_name,
                "name_zh": name_zh,
                "url": info.get("url", ""),
                "jurisdiction": jurisdiction,
                "type": info.get("type") or info.get("category", ""),
                "source": f"內建{jurisdiction}法規資料庫",
            }
            # 加入額外欄位（如 celex, pcode）
            for key in ["celex", "pcode"]:
                if key in info:
                    result[key] = info[key]
            matched.append(result)

    return matched


# ===== Web 搜尋工具 =====

def _google_search(
    query: str,
    num_results: int = 5,
    language: str | None = None,
    country: str | None = None,
    date_restrict: str | None = None,
    file_type: str | None = None,
    exact_terms: str | None = None,
    exclude_terms: str | None = None,
    or_terms: str | None = None,
    start_index: int = 1,
    site_search: str | None = None,
    site_search_filter: str | None = None,
    sort: str | None = None,
    filter_duplicates: str | None = None,
    geolocation: str | None = None,
    interface_language: str | None = None,
    link_site: str | None = None,
    safe: str = "off",
    c2coff: str | None = None,
    low_range: str | None = None,
    high_range: str | None = None,
) -> list[dict] | None:
    """
    使用 Google Custom Search API 進行搜尋

    Args:
        query: 搜尋關鍵字
        num_results: 返回結果數量（1-10）
        language: 限制語言 (lr)，如 "lang_ja"（日文）、"lang_ko"（韓文）、"lang_zh-TW"（繁中）
        country: 限制國家 (cr)，如 "countryJP"（日本）、"countryKR"（韓國）
        date_restrict: 時間限制，如 "y1"（1年內）、"m6"（6個月內）、"w2"（2週內）、"d10"（10天內）
        file_type: 檔案類型，如 "pdf"、"doc"、"xls"
        exact_terms: 必須包含的精確詞彙
        exclude_terms: 排除的詞彙
        or_terms: 至少包含其中一個詞彙（OR 搜尋）
        start_index: 起始索引（用於分頁，1-91）
        site_search: 限制特定網站（比查詢中的 site: 更精確）
        site_search_filter: 網站搜尋模式，"i"=包含，"e"=排除
        sort: 排序方式，如 "date"（按日期排序）
        filter_duplicates: 重複內容過濾，"0"=關閉（顯示更多），"1"=開啟
        geolocation: 使用者地理位置 (gl)，如 "kr"、"jp"、"tw"（小寫兩字母）
        interface_language: 介面語言 (hl)，影響 snippet 語言，支援更多語言如 "th"、"vi"
        link_site: 結果必須連結到此網址
        safe: 安全搜尋，"active"=開啟，"off"=關閉（預設）
        c2coff: 停用簡繁中文轉換，"1"=停用，"0"=啟用（預設）
        low_range: 數字範圍搜尋下限
        high_range: 數字範圍搜尋上限

    Returns:
        搜尋結果列表，或 None（若未設定 API Key 或發生錯誤）
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        return None

    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": min(num_results, 10),  # Google API 最多一次返回 10 筆
            "start": start_index,
            "safe": safe,  # 預設關閉安全搜尋
        }

        # ===== 語言與地區參數 =====
        if language:
            params["lr"] = language  # 語言限制（搜尋結果語言）
        if country:
            params["cr"] = country  # 國家限制（搜尋結果來源國家）
        if geolocation:
            params["gl"] = geolocation  # 使用者地理位置（影響結果排序）
        if interface_language:
            params["hl"] = interface_language  # 介面語言（影響 snippet 語言）

        # ===== 時間與檔案類型參數 =====
        if date_restrict:
            params["dateRestrict"] = date_restrict  # 時間限制
        if file_type:
            params["fileType"] = file_type  # 檔案類型

        # ===== 關鍵字控制參數 =====
        if exact_terms:
            params["exactTerms"] = exact_terms  # 必須包含
        if exclude_terms:
            params["excludeTerms"] = exclude_terms  # 排除詞彙
        if or_terms:
            params["orTerms"] = or_terms  # 至少包含其中一個

        # ===== 網站限制參數 =====
        if site_search:
            params["siteSearch"] = site_search  # 限制特定網站
        if site_search_filter:
            params["siteSearchFilter"] = site_search_filter  # 包含/排除模式

        # ===== 排序與過濾參數 =====
        if sort:
            params["sort"] = sort  # 排序方式
        if filter_duplicates is not None:
            params["filter"] = filter_duplicates  # 重複內容過濾

        # ===== 進階參數 =====
        if link_site:
            params["linkSite"] = link_site  # 必須連結到此網址
        if c2coff:
            params["c2coff"] = c2coff  # 簡繁中文轉換控制
        if low_range:
            params["lowRange"] = low_range  # 數字範圍下限
        if high_range:
            params["highRange"] = high_range  # 數字範圍上限

        with _get_http_client(timeout=30) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        items = data.get("items", [])
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            }
            for item in items
        ]

    except Exception as e:
        print(f"[web_search] Google API 錯誤: {e}，回退到 DuckDuckGo")
        return None


def _duckduckgo_search(query: str, num_results: int = 5) -> list[dict]:
    """
    使用 DuckDuckGo 進行搜尋（備用方案）

    Returns:
        搜尋結果列表
    """
    from ddgs import DDGS

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=num_results))

    return [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "snippet": r.get("body", ""),
        }
        for r in results
    ]


def web_search(
    query: Annotated[str, "搜尋關鍵字"],
    region: Annotated[str, "目標地區，例如：台灣、日本、歐盟、韓國、印度、巴西、越南"] = "全球",
    num_results: Annotated[int, "返回結果數量"] = 10,
    date_restrict: Annotated[str | None, "時間限制：y1（1年內）、m6（6個月內）、w2（2週內）、d10（10天內）"] = None,
    file_type: Annotated[str | None, "檔案類型：pdf、doc、xls"] = None,
    exact_terms: Annotated[str | None, "必須包含的精確詞彙"] = None,
    exclude_terms: Annotated[str | None, "排除的詞彙（如：草案、draft）"] = None,
    or_terms: Annotated[str | None, "至少包含其中一個詞彙（OR 搜尋）"] = None,
    sort_by_date: Annotated[bool, "是否按日期排序（找最新法規）"] = False,
    disable_duplicate_filter: Annotated[bool, "關閉重複過濾（顯示更多結果）"] = False,
) -> str:
    """
    搜尋法規相關資訊。

    優先使用 Google Custom Search API（若已設定），否則使用 DuckDuckGo。
    支援多種進階參數以精確控制搜尋結果。

    Returns:
        JSON 格式的搜尋結果
    """
    # REGION_CONFIG 從 config/regions.yaml 載入（模組層級）
    # 參考: https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list

    # 取得地區設定（使用模組層級的 REGION_CONFIG）
    config = REGION_CONFIG.get(region, {})
    site_filter = config.get("sites", "")
    language = config.get("language")
    country = config.get("country")
    geolocation = config.get("geolocation")
    interface_lang = config.get("interface_lang")
    c2coff = config.get("c2coff")

    # 增強查詢（加入地區網站限制）
    enhanced_query = query
    if site_filter:
        enhanced_query = f"{query} {site_filter}"

    try:
        # 優先使用 Google Custom Search API（帶進階參數）
        results = _google_search(
            enhanced_query,
            num_results=num_results,
            language=language,
            country=country,
            date_restrict=date_restrict,
            file_type=file_type,
            exact_terms=exact_terms,
            exclude_terms=exclude_terms,
            or_terms=or_terms,
            geolocation=geolocation,
            interface_language=interface_lang,
            sort="date" if sort_by_date else None,
            filter_duplicates="0" if disable_duplicate_filter else None,
            c2coff=c2coff,
        )
        search_engine = "Google Custom Search"

        # 若 Google 不可用，回退到 DuckDuckGo
        if results is None:
            results = _duckduckgo_search(enhanced_query, num_results)
            search_engine = "DuckDuckGo"

        # 日誌輸出：顯示使用的搜尋引擎
        print(f"[web_search] 使用 {search_engine}，查詢: {query[:50]}...，結果: {len(results)} 筆")

        return _json_response("success", {
            "query": query,
            "region": region,
            "search_engine": search_engine,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        })

    except ImportError:
        return _json_response("error", error="搜尋套件未安裝，請執行: pip install ddgs")
    except Exception as e:
        return _json_response("error", error=str(e))


# ===== 台灣法規爬蟲工具 =====

def search_tw_laws(
    query: Annotated[str, "搜尋關鍵字，例如：個人資料保護"],
    limit: Annotated[int, "返回結果數量上限"] = 10,
) -> str:
    """
    搜尋台灣全國法規資料庫。

    支援的法規類別：個資、資安、金融、電信、醫療
    常用法規：個人資料保護法、資通安全管理法、電子簽章法等

    Returns:
        JSON 格式的搜尋結果
    """
    from ..crawlers.tw_laws import COMMON_TW_LAWS, TW_LAW_CATEGORIES

    CATEGORY_KEYWORDS = {
        "個資": ["個資", "個人資料", "隱私", "pdpa"],
        "資安": ["資安", "資通安全", "網路安全", "cybersecurity", "資訊安全"],
        "金融": ["金融", "銀行", "保險", "證券", "電子銀行"],
        "電信": ["電信", "通訊", "網路"],
        "醫療": ["醫療", "電子病歷", "健康資料"],
    }

    async def _search():
        from ..crawlers.tw_laws import TaiwanLawsCrawler
        async with TaiwanLawsCrawler() as crawler:
            return await crawler.search(query, limit=limit)

    def _fallback_search() -> list[dict]:
        """網站搜尋失敗時的後備搜尋"""
        matched_laws = []
        query_lower = query.lower()

        # 1. 先檢查類別關鍵字匹配
        matched_categories = [
            cat for cat, keywords in CATEGORY_KEYWORDS.items()
            if any(kw in query_lower or kw in query for kw in keywords)
        ]

        # 2. 從匹配的類別中提取法規
        if matched_categories:
            for cat in matched_categories:
                for law_name in TW_LAW_CATEGORIES.get(cat, []):
                    if law_name in COMMON_TW_LAWS:
                        pcode = COMMON_TW_LAWS[law_name]
                        matched_laws.append({
                            "title": law_name,
                            "pcode": pcode,
                            "url": f"https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={pcode}",
                            "jurisdiction": "台灣",
                            "type": "法律/法規命令",
                            "category": cat,
                            "source": "內建法規資料庫"
                        })

        # 3. 如果沒有類別匹配，進行關鍵字匹配
        if not matched_laws:
            for law_name, pcode in COMMON_TW_LAWS.items():
                if any(keyword in law_name for keyword in query.split()):
                    matched_laws.append({
                        "title": law_name,
                        "pcode": pcode,
                        "url": f"https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={pcode}",
                        "jurisdiction": "台灣",
                        "type": "法律/法規命令",
                        "source": "內建法規資料庫"
                    })

        # 去重
        seen_pcodes = set()
        return [
            law for law in matched_laws
            if law['pcode'] not in seen_pcodes and not seen_pcodes.add(law['pcode'])
        ][:limit]

    try:
        results = asyncio.run(_search())
        if not results:
            results = _fallback_search()

        return _json_response("success", {
            "source": "全國法規資料庫",
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return _json_response("error", error=str(e))


def fetch_tw_law_content(
    pcode: Annotated[str, "法規代碼，例如：I0050021 (個人資料保護法)"],
) -> str:
    """
    取得台灣法規的完整內容。

    常用法規代碼：
    - I0050021: 個人資料保護法
    - A0030297: 資通安全管理法
    - J0080037: 電子簽章法

    Returns:
        JSON 格式的法規內容
    """
    async def _fetch():
        from ..crawlers.tw_laws import TaiwanLawsCrawler
        async with TaiwanLawsCrawler() as crawler:
            result = await crawler.get_regulation(pcode)
            return result.to_dict()

    try:
        result = asyncio.run(_fetch())
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return _json_response("error", error=str(e))


# ===== 通用網頁抓取工具 =====

MAX_TEXT_LENGTH = 10000
MAX_HTML_LENGTH = 20000


def fetch_webpage(
    url: Annotated[str, "要抓取的網頁 URL"],
    extract_text: Annotated[bool, "是否只提取文字內容"] = True,
) -> str:
    """
    抓取網頁內容。

    Returns:
        網頁內容（HTML 或純文字）
    """
    # URL 安全性驗證
    is_valid, error_msg = _validate_url(url)
    if not is_valid:
        return _json_response("error", {"url": url}, error=error_msg)

    try:
        with _get_http_client() as client:
            response = client.get(url)
            response.raise_for_status()

            if extract_text:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "lxml")

                # 移除非內容標籤
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()

                text = soup.get_text(separator="\n", strip=True)
                if len(text) > MAX_TEXT_LENGTH:
                    text = text[:MAX_TEXT_LENGTH] + "\n... (內容已截斷)"

                return _json_response("success", {
                    "url": url,
                    "content": text,
                    "content_type": "text",
                    "timestamp": datetime.now().isoformat(),
                })
            else:
                return _json_response("success", {
                    "url": url,
                    "content": response.text[:MAX_HTML_LENGTH],
                    "content_type": "html",
                    "timestamp": datetime.now().isoformat(),
                })

    except Exception as e:
        return _json_response("error", {"url": url}, error=str(e))


# ===== PDF 解析工具 =====

def fetch_pdf_content(
    url: Annotated[str, "PDF 檔案 URL"],
    max_pages: Annotated[int, "最多解析頁數"] = 10,
    max_chars: Annotated[int, "最大字元數"] = 5000,
) -> str:
    """
    下載並解析 PDF 檔案內容。

    Returns:
        JSON 格式的 PDF 文字內容
    """
    # URL 安全性驗證
    is_valid, error_msg = _validate_url(url)
    if not is_valid:
        return _json_response("error", {"url": url}, error=error_msg)

    import os
    import tempfile

    try:
        # 下載 PDF 到暫存檔
        with _get_http_client(timeout=60) as client:
            response = client.get(url)
            response.raise_for_status()

            # 確認是 PDF
            content_type = response.headers.get("content-type", "")
            if "pdf" not in content_type.lower() and not url.endswith(".pdf"):
                return _json_response("error", {"url": url}, error=f"非 PDF 檔案: {content_type}")

            # 寫入暫存檔
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name

        # 使用 pdfplumber 解析 PDF
        try:
            import pdfplumber

            text_parts = []
            with pdfplumber.open(tmp_path) as pdf:
                total_pages = len(pdf.pages)
                pages_to_read = min(max_pages, total_pages)

                for i in range(pages_to_read):
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        text_parts.append(f"[第 {i+1} 頁]\n{page_text}")

            full_text = "\n\n".join(text_parts)
            if len(full_text) > max_chars:
                full_text = full_text[:max_chars] + "\n... (內容已截斷)"

            return _json_response("success", {
                "url": url,
                "content": full_text,
                "content_type": "pdf",
                "total_pages": total_pages,
                "pages_extracted": pages_to_read,
                "timestamp": datetime.now().isoformat(),
            })

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except ImportError:
        return _json_response("error", {"url": url}, error="pdfplumber 套件未安裝，請執行: pip install pdfplumber")
    except Exception as e:
        return _json_response("error", {"url": url}, error=str(e))


# ===== 日本法規搜尋工具 =====

# 日本常用資安/個資相關法規資料庫
# ===== 日本法規類別定義（用於「所有」「相關」查詢）=====
JP_LAW_CATEGORIES = {
    "資安": ["資安", "資訊安全", "網路安全", "cybersecurity", "サイバー", "情報セキュリティ", "security"],
    "個資": ["個資", "個人資料", "隱私", "privacy", "個人情報"],
    "金融": ["金融", "銀行", "證券", "保險", "FSA", "金融庁"],
}

JP_COMMON_LAWS = {
    # ===== 資安相關法規 =====
    "サイバーセキュリティ基本法": {
        "name_zh": "網路安全基本法",
        "url": "https://elaws.e-gov.go.jp/document?lawid=426AC1000000104",
        "type": "法律",
        "category": "資安",
        "keywords": ["資安", "資訊安全", "cybersecurity", "サイバー", "網路安全", "情報セキュリティ"],
    },
    "不正アクセス禁止法": {
        "name_zh": "禁止非法存取法",
        "url": "https://elaws.e-gov.go.jp/document?lawid=411AC0000000128",
        "type": "法律",
        "category": "資安",
        "keywords": ["資安", "資訊安全", "非法存取", "不正アクセス", "hacking"],
    },
    "電気通信事業法": {
        "name_zh": "電信事業法",
        "url": "https://elaws.e-gov.go.jp/document?lawid=359AC0000000086",
        "type": "法律",
        "category": "資安",
        "keywords": ["資安", "資訊安全", "電信", "通訊", "電気通信", "網路"],
    },
    "刑法（コンピュータ犯罪関連条文）": {
        "name_zh": "刑法（電腦犯罪相關條文）",
        "url": "https://elaws.e-gov.go.jp/document?lawid=140AC0000000045",
        "type": "法律",
        "category": "資安",
        "keywords": ["資安", "資訊安全", "犯罪", "刑法", "電腦犯罪", "サイバー犯罪"],
    },

    # ===== 金融資安相關法規（FSA 金融廳）=====
    "金融分野におけるサイバーセキュリティに関するガイドライン": {
        "name_zh": "金融領域網路安全指引",
        "url": "https://www.fsa.go.jp/news/r6/sonota/20241004/18.pdf",
        "type": "ガイドライン",
        "category": "資安",
        "authority": "金融庁（FSA）",
        "issue_date": "2024/10/4",
        "keywords": ["資安", "資訊安全", "金融", "銀行", "サイバー", "FSA", "金融庁"],
    },
    "暗号資産交換業者関係": {
        "name_zh": "加密資產交換業者監督指引",
        "url": "https://www.fsa.go.jp/common/law/guide/kaisya/16.pdf",
        "type": "ガイドライン",
        "category": "資安",
        "authority": "金融庁（FSA）",
        "issue_date": "2021/6",
        "keywords": ["資安", "資訊安全", "金融", "暗号資産", "加密貨幣", "虛擬貨幣", "crypto", "FSA"],
    },
    "金融商品取引業者等向けの総合的な監督指針": {
        "name_zh": "金融商品交易業者綜合監督指引",
        "url": "https://www.fsa.go.jp/common/law/guide/kinyushohin/",
        "type": "ガイドライン",
        "category": "資安",
        "authority": "金融庁（FSA）",
        "issue_date": "2024/5/18",
        "keywords": ["資安", "資訊安全", "金融", "證券", "金融商品", "監督", "FSA"],
    },
    "主要行等向けの総合的な監督指針": {
        "name_zh": "主要銀行綜合監督指引",
        "url": "https://www.fsa.go.jp/common/law/guide/city/",
        "type": "ガイドライン",
        "category": "資安",
        "authority": "金融庁（FSA）",
        "issue_date": "2024/5/18",
        "keywords": ["資安", "資訊安全", "金融", "銀行", "主要行", "監督", "FSA"],
    },
    "金融機関におけるコンピュータシステムの安全対策基準": {
        "name_zh": "金融機構電腦系統安全對策基準",
        "url": "https://www.fsa.go.jp/",
        "type": "ガイドライン",
        "category": "資安",
        "authority": "金融庁（FSA）",
        "keywords": ["資安", "資訊安全", "金融", "系統安全", "銀行", "コンピュータ"],
    },

    # ===== 個資相關法規 =====
    "個人情報保護法": {
        "name_zh": "個人資料保護法",
        "url": "https://elaws.e-gov.go.jp/document?lawid=415AC0000000057",
        "type": "法律",
        "category": "個資",
        "keywords": ["個資", "個人資料", "個人情報", "privacy", "隱私", "data protection"],
    },
    "行政機関個人情報保護法": {
        "name_zh": "行政機關個人資料保護法",
        "url": "https://elaws.e-gov.go.jp/document?lawid=415AC0000000058",
        "type": "法律",
        "category": "個資",
        "keywords": ["個資", "個人資料", "行政機關", "個人情報", "政府"],
    },

    # ===== 其他資安相關 =====
    "経済安全保障推進法": {
        "name_zh": "經濟安全保障推進法",
        "url": "https://elaws.e-gov.go.jp/document?lawid=504AC0000000043",
        "type": "法律",
        "category": "資安",
        "keywords": ["資安", "資訊安全", "經濟安全", "供應鏈", "重要基礎設施"],
    },
    "重要インフラのサイバーセキュリティに係る行動計画": {
        "name_zh": "重要基礎設施網路安全行動計畫",
        "url": "https://www.nisc.go.jp/",
        "type": "計画",
        "category": "資安",
        "authority": "NISC",
        "keywords": ["資安", "資訊安全", "重要基礎設施", "關鍵基礎設施", "NISC", "サイバー"],
    },
}


def _is_broad_query(query: str) -> bool:
    """檢查是否為廣泛查詢（包含「所有」「全部」「相關」等詞）"""
    broad_keywords = ["所有", "全部", "相關", "有哪些", "列出", "all", "全て", "すべて"]
    query_lower = query.lower()
    return any(kw in query_lower for kw in broad_keywords)


def _get_category_from_query(query: str) -> str | None:
    """從查詢中識別法規類別"""
    query_lower = query.lower()
    for category, keywords in JP_LAW_CATEGORIES.items():
        if any(kw in query_lower for kw in keywords):
            return category
    return None


def _match_laws_by_category(category: str, laws_db: dict, jurisdiction: str) -> list[dict]:
    """根據類別返回所有相關法規"""
    matched = []
    for law_name, info in laws_db.items():
        if info.get("category") == category:
            result = {
                "title": law_name,
                "name_zh": info.get("name_zh", ""),
                "url": info.get("url", ""),
                "jurisdiction": jurisdiction,
                "type": info.get("type", ""),
                "category": category,
                "source": f"內建{jurisdiction}法規資料庫",
            }
            # 加入額外欄位
            for key in ["authority", "issue_date"]:
                if key in info:
                    result[key] = info[key]
            matched.append(result)
    return matched


def search_jp_laws(
    query: Annotated[str, "搜尋關鍵字（日文或中文）"],
    category: Annotated[str, "法規類別：法律、政令、府令、規則"] = "all",
) -> str:
    """
    搜尋日本法規。

    **增強功能**：
    - 當查詢包含「所有」「相關」時，返回整個類別的法規
    - 同時搜尋內建資料庫和 Web，確保結果全面
    - 支援的領域：資安、個資、金融、電信

    Returns:
        JSON 格式的搜尋結果
    """
    all_results = []

    # 1. 檢查是否為廣泛查詢（如「日本資訊安全相關法規」）
    is_broad = _is_broad_query(query)
    detected_category = _get_category_from_query(query)

    # 2. 內建資料庫搜尋
    if is_broad and detected_category:
        # 廣泛查詢：返回整個類別
        matched_laws = _match_laws_by_category(detected_category, JP_COMMON_LAWS, "日本")
        print(f"[search_jp_laws] 廣泛查詢，類別: {detected_category}，找到 {len(matched_laws)} 筆")
    else:
        # 精確查詢：關鍵字匹配
        matched_laws = _match_laws_by_keywords(query, JP_COMMON_LAWS, "日本")
        print(f"[search_jp_laws] 精確查詢，找到 {len(matched_laws)} 筆")

    all_results.extend(matched_laws)

    # 3. 同時執行 Web 搜尋以補充結果
    try:
        enhanced_query = f"{query} site:elaws.e-gov.go.jp OR site:fsa.go.jp OR site:nisc.go.jp"
        web_result_str = web_search(enhanced_query, region="日本", num_results=10)
        web_data = json.loads(web_result_str)

        if web_data.get("status") == "success":
            web_results = web_data.get("results", [])
            # 標記來源並加入（避免重複）
            existing_urls = {r.get("url") for r in all_results}
            for wr in web_results:
                if wr.get("url") not in existing_urls:
                    wr["source"] = "Web 搜尋"
                    wr["jurisdiction"] = "日本"
                    all_results.append(wr)
            print(f"[search_jp_laws] Web 搜尋補充 {len(web_results)} 筆")
    except Exception as e:
        print(f"[search_jp_laws] Web 搜尋失敗: {e}")

    if all_results:
        return _json_response("success", {
            "source": "日本法規資料庫（內建 + Web 搜尋）",
            "query": query,
            "results": all_results,
            "count": len(all_results),
            "db_count": len(matched_laws),
            "web_count": len(all_results) - len(matched_laws),
            "timestamp": datetime.now().isoformat(),
        })

    return _json_response("success", {
        "source": "日本法規資料庫",
        "query": query,
        "results": [],
        "count": 0,
        "message": "未找到符合的法規，請嘗試其他關鍵字",
        "timestamp": datetime.now().isoformat(),
    })


# ===== 歐盟法規搜尋工具 =====

# 歐盟常用資安/個資相關法規資料庫
EU_COMMON_LAWS = {
    "General Data Protection Regulation (GDPR)": {
        "name_zh": "一般資料保護規則",
        "celex": "32016R0679",
        "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        "type": "Regulation",
        "keywords": ["gdpr", "資料保護", "個資", "privacy", "data protection"],
    },
    "ePrivacy Directive": {
        "name_zh": "電子通訊隱私指令",
        "celex": "32002L0058",
        "url": "https://eur-lex.europa.eu/eli/dir/2002/58/oj",
        "type": "Directive",
        "keywords": ["eprivacy", "cookie", "電子通訊", "隱私"],
    },
    "NIS 2 Directive": {
        "name_zh": "網路與資訊系統安全指令 2.0",
        "celex": "32022L2555",
        "url": "https://eur-lex.europa.eu/eli/dir/2022/2555/oj",
        "type": "Directive",
        "keywords": ["nis", "資安", "網路安全", "cybersecurity", "關鍵基礎設施"],
    },
    "Cybersecurity Act": {
        "name_zh": "網路安全法案",
        "celex": "32019R0881",
        "url": "https://eur-lex.europa.eu/eli/reg/2019/881/oj",
        "type": "Regulation",
        "keywords": ["cybersecurity", "資安", "enisa", "認證"],
    },
    "Cyber Resilience Act": {
        "name_zh": "網路韌性法案",
        "celex": "52022PC0454",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:52022PC0454",
        "type": "Proposal",
        "keywords": ["cyber resilience", "IoT", "產品安全", "韌性"],
    },
    "Digital Services Act (DSA)": {
        "name_zh": "數位服務法",
        "celex": "32022R2065",
        "url": "https://eur-lex.europa.eu/eli/reg/2022/2065/oj",
        "type": "Regulation",
        "keywords": ["dsa", "數位服務", "平台", "內容審核"],
    },
    "Digital Markets Act (DMA)": {
        "name_zh": "數位市場法",
        "celex": "32022R1925",
        "url": "https://eur-lex.europa.eu/eli/reg/2022/1925/oj",
        "type": "Regulation",
        "keywords": ["dma", "數位市場", "守門人", "平台"],
    },
    "AI Act": {
        "name_zh": "人工智慧法案",
        "celex": "52021PC0206",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:52021PC0206",
        "type": "Regulation",
        "keywords": ["ai", "人工智慧", "機器學習", "artificial intelligence"],
    },
    "Digital Operational Resilience Act (DORA)": {
        "name_zh": "數位營運韌性法案",
        "celex": "32022R2554",
        "url": "https://eur-lex.europa.eu/eli/reg/2022/2554/oj",
        "type": "Regulation",
        "keywords": ["dora", "金融", "韌性", "資安", "fintech"],
    },
    "PSD2 (Payment Services Directive 2)": {
        "name_zh": "支付服務指令第二版",
        "celex": "32015L2366",
        "url": "https://eur-lex.europa.eu/eli/dir/2015/2366/oj",
        "type": "Directive",
        "keywords": ["psd2", "支付", "open banking", "金融"],
    },
}


def search_eu_laws(
    query: Annotated[str, "搜尋關鍵字"],
    doc_type: Annotated[str, "文件類型：regulation、directive、decision"] = "all",
) -> str:
    """
    搜尋歐盟 EUR-Lex 法規資料庫。

    支援的領域：資料保護、網路安全、數位市場
    常用法規：GDPR、NIS Directive、ePrivacy 等

    Returns:
        JSON 格式的搜尋結果
    """
    matched_laws = _match_laws_by_keywords(query, EU_COMMON_LAWS, "歐盟")

    # 過濾文件類型
    if doc_type != "all" and matched_laws:
        matched_laws = [
            law for law in matched_laws
            if law["type"].lower() == doc_type.lower()
        ]

    if matched_laws:
        return _json_response("success", {
            "source": "歐盟法規資料庫（內建 + EUR-Lex）",
            "query": query,
            "results": matched_laws,
            "count": len(matched_laws),
            "timestamp": datetime.now().isoformat(),
        })

    # 沒有匹配則使用 web_search
    enhanced_query = f"{query} site:eur-lex.europa.eu"
    if doc_type != "all":
        enhanced_query += f" {doc_type}"
    return web_search(enhanced_query, region="歐盟", num_results=10)


# ===== 工具註冊表 =====

AVAILABLE_TOOLS = [
    web_search,
    search_tw_laws,
    fetch_tw_law_content,
    fetch_webpage,
    fetch_pdf_content,
    search_jp_laws,
    search_eu_laws,
]


def get_tool_descriptions() -> str:
    """取得所有工具的描述"""
    descriptions = []
    for tool in AVAILABLE_TOOLS:
        doc = tool.__doc__ or ""
        first_line = doc.strip().split("\n")[0] if doc else "無描述"
        descriptions.append(f"- {tool.__name__}: {first_line}")
    return "\n".join(descriptions)
