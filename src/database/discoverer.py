"""
法規自動發現模組

提供:
- 爬取各國監管機構網站發現新法規
- 使用 Google Search 搜尋最新法規動態
- LLM 解析爬取內容提取法規資訊
- 自動比對並新增資料庫中沒有的法規
"""

import json
import time
import re
from datetime import datetime
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass

from .manager import BaselineManager
from .models import RegulationBaseline, get_session


# === 監管機構網站清單 ===

REGULATORY_SOURCES = {
    # 台灣
    "TW": [
        {
            "name": "金融監督管理委員會",
            "name_en": "Financial Supervisory Commission",
            "url": "https://www.fsc.gov.tw",
            "search_queries": [
                "金管會 資安 法規 最新",
                "金管會 個資 法規 2024",
                "台灣 金融資安 新規定",
            ],
            "industries": ["finance_general", "banking", "securities", "insurance"],
        },
        {
            "name": "數位發展部",
            "name_en": "Ministry of Digital Affairs",
            "url": "https://moda.gov.tw",
            "search_queries": [
                "數位發展部 資通安全 法規",
                "台灣 資安法 修正",
            ],
            "industries": ["technology", "telecom"],
        },
        {
            "name": "國家通訊傳播委員會",
            "name_en": "National Communications Commission",
            "url": "https://www.ncc.gov.tw",
            "search_queries": [
                "NCC 電信 資安 法規",
            ],
            "industries": ["telecom"],
        },
    ],
    # 日本
    "JP": [
        {
            "name": "金融庁",
            "name_en": "Financial Services Agency",
            "url": "https://www.fsa.go.jp",
            "search_queries": [
                "金融庁 サイバーセキュリティ ガイドライン 最新",
                "金融庁 情報セキュリティ 監督指針",
            ],
            "industries": ["finance_general", "banking", "securities", "insurance"],
        },
        {
            "name": "個人情報保護委員会",
            "name_en": "Personal Information Protection Commission",
            "url": "https://www.ppc.go.jp",
            "search_queries": [
                "個人情報保護法 改正 最新",
            ],
            "industries": ["finance_general", "healthcare", "technology"],
        },
    ],
    # 新加坡
    "SG": [
        {
            "name": "Monetary Authority of Singapore",
            "name_en": "MAS",
            "url": "https://www.mas.gov.sg",
            "search_queries": [
                "MAS technology risk management guidelines latest",
                "MAS cybersecurity notice 2024",
                "MAS TRM guidelines update",
            ],
            "industries": ["finance_general", "banking", "securities", "insurance", "fintech"],
        },
        {
            "name": "Personal Data Protection Commission",
            "name_en": "PDPC",
            "url": "https://www.pdpc.gov.sg",
            "search_queries": [
                "Singapore PDPA amendment latest",
            ],
            "industries": ["finance_general", "technology", "healthcare"],
        },
    ],
    # 香港
    "HK": [
        {
            "name": "Hong Kong Monetary Authority",
            "name_en": "HKMA",
            "url": "https://www.hkma.gov.hk",
            "search_queries": [
                "HKMA technology risk supervisory policy manual",
                "HKMA cybersecurity circular latest",
            ],
            "industries": ["finance_general", "banking"],
        },
    ],
    # 歐盟
    "EU": [
        {
            "name": "European Commission",
            "name_en": "EC",
            "url": "https://ec.europa.eu",
            "search_queries": [
                "EU DORA regulation implementation",
                "EU NIS2 directive latest",
                "EU AI Act regulation",
                "EU Cyber Resilience Act",
            ],
            "industries": ["finance_general", "technology", "healthcare", "energy"],
        },
        {
            "name": "European Banking Authority",
            "name_en": "EBA",
            "url": "https://www.eba.europa.eu",
            "search_queries": [
                "EBA ICT risk guidelines latest",
                "EBA outsourcing guidelines",
            ],
            "industries": ["banking", "finance_general"],
        },
    ],
    # 美國
    "US": [
        {
            "name": "Securities and Exchange Commission",
            "name_en": "SEC",
            "url": "https://www.sec.gov",
            "search_queries": [
                "SEC cybersecurity disclosure rule 2024",
                "SEC cyber risk management regulation",
            ],
            "industries": ["securities", "finance_general"],
        },
        {
            "name": "Federal Financial Institutions Examination Council",
            "name_en": "FFIEC",
            "url": "https://www.ffiec.gov",
            "search_queries": [
                "FFIEC cybersecurity handbook update",
                "FFIEC IT examination handbook latest",
            ],
            "industries": ["banking", "finance_general"],
        },
        {
            "name": "New York Department of Financial Services",
            "name_en": "NYDFS",
            "url": "https://www.dfs.ny.gov",
            "search_queries": [
                "23 NYCRR 500 amendment 2024",
                "NYDFS cybersecurity regulation update",
            ],
            "industries": ["finance_general", "insurance"],
        },
    ],
    # 澳洲
    "AU": [
        {
            "name": "Australian Prudential Regulation Authority",
            "name_en": "APRA",
            "url": "https://www.apra.gov.au",
            "search_queries": [
                "APRA CPS 234 update",
                "APRA CPS 230 operational resilience",
                "APRA information security standard",
            ],
            "industries": ["banking", "insurance", "finance_general"],
        },
    ],
    # 韓國
    "KR": [
        {
            "name": "금융위원회",
            "name_en": "Financial Services Commission",
            "url": "https://www.fsc.go.kr",
            "search_queries": [
                "금융위원회 전자금융 규정 최신",
                "금융보안원 사이버보안 가이드라인",
            ],
            "industries": ["finance_general", "banking", "fintech"],
        },
    ],
    # 中國
    "CN": [
        {
            "name": "中国人民银行",
            "name_en": "People's Bank of China",
            "url": "http://www.pbc.gov.cn",
            "search_queries": [
                "人民银行 金融数据安全 规定 最新",
                "银保监会 信息科技 监管",
            ],
            "industries": ["banking", "finance_general"],
        },
        {
            "name": "国家互联网信息办公室",
            "name_en": "Cyberspace Administration of China",
            "url": "http://www.cac.gov.cn",
            "search_queries": [
                "网信办 数据安全 法规 最新",
                "个人信息保护法 实施细则",
            ],
            "industries": ["technology", "finance_general"],
        },
    ],
}


@dataclass
class DiscoveredRegulation:
    """發現的法規資料結構"""
    name: str
    name_en: Optional[str] = None
    name_zh: Optional[str] = None
    country_code: str = ""
    industry_code: str = "finance_general"
    topic_code: str = "cybersecurity"
    regulation_type: Optional[str] = None
    issuing_authority: Optional[str] = None
    official_url: Optional[str] = None
    summary: Optional[str] = None
    search_keywords: List[str] = None
    applicable_industries: List[str] = None
    confidence_score: float = 0.5
    source_query: str = ""

    def __post_init__(self):
        if self.search_keywords is None:
            self.search_keywords = [self.name]
        if self.applicable_industries is None:
            self.applicable_industries = [self.industry_code]


class RegulationDiscoverer:
    """法規自動發現器"""

    def __init__(
        self,
        search_function: Optional[Callable] = None,
        fetch_function: Optional[Callable] = None,
        llm_function: Optional[Callable] = None,
        status_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        初始化發現器

        Args:
            search_function: 網路搜尋函數 (預設使用 web_search)
            fetch_function: 網頁爬取函數 (預設使用 fetch_url)
            llm_function: LLM 解析函數 (預設使用 Azure OpenAI)
            status_callback: 狀態回調函數
        """
        self.manager = BaselineManager()
        self.status_callback = status_callback or (lambda x: print(x))

        # 預設搜尋函數
        if search_function is None:
            from ..agents.tools import web_search
            self.search_function = web_search
        else:
            self.search_function = search_function

        # 預設爬取函數
        if fetch_function is None:
            from ..agents.tools import fetch_webpage
            self.fetch_function = fetch_webpage
        else:
            self.fetch_function = fetch_function

        # 預設 LLM 函數
        if llm_function is None:
            self.llm_function = self._default_llm_parse
        else:
            self.llm_function = llm_function

    def _report(self, message: str):
        """報告狀態"""
        self.status_callback(message)

    def _default_llm_parse(self, content: str, prompt: str) -> str:
        """預設 LLM 解析函數"""
        try:
            from openai import AzureOpenAI
            import os

            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )

            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "你是法規分析專家，擅長從網頁內容中提取法規資訊。"},
                    {"role": "user", "content": f"{prompt}\n\n---\n內容:\n{content[:8000]}"},
                ],
                temperature=0.1,
                max_tokens=2000,
            )

            return response.choices[0].message.content

        except Exception as e:
            self._report(f"  ⚠️ LLM 解析失敗: {str(e)[:50]}")
            return ""

    def _is_regulation_exists(self, name: str, country_code: str) -> bool:
        """檢查法規是否已存在於資料庫"""
        session = get_session()

        # 模糊比對：名稱相似度
        existing = session.query(RegulationBaseline).filter(
            RegulationBaseline.country_code == country_code,
            RegulationBaseline.is_active == True,
        ).all()

        session.close()

        # 檢查名稱是否相似
        name_lower = name.lower().strip()
        for reg in existing:
            existing_name = reg.name.lower().strip()
            existing_en = (reg.name_en or "").lower().strip()
            existing_zh = (reg.name_zh or "").lower().strip()

            # 完全匹配
            if name_lower in [existing_name, existing_en, existing_zh]:
                return True

            # 部分匹配（超過 80% 相似）
            if self._similarity(name_lower, existing_name) > 0.8:
                return True
            if existing_en and self._similarity(name_lower, existing_en) > 0.8:
                return True
            if existing_zh and self._similarity(name_lower, existing_zh) > 0.8:
                return True

        return False

    def _similarity(self, s1: str, s2: str) -> float:
        """計算兩個字串的相似度（簡單版本）"""
        if not s1 or not s2:
            return 0.0

        # 使用 Jaccard 相似度
        set1 = set(s1.split())
        set2 = set(s2.split())

        if not set1 or not set2:
            # 如果無法分詞，使用字元級別比對
            set1 = set(s1)
            set2 = set(s2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _parse_search_results(
        self,
        search_results: List[Dict],
        country_code: str,
        source_info: Dict,
    ) -> List[DiscoveredRegulation]:
        """解析搜尋結果，提取法規資訊"""
        discovered = []

        for result in search_results[:5]:  # 只處理前 5 筆結果
            title = result.get("title", "")
            url = result.get("url", "")
            snippet = result.get("snippet", "")

            if not title:
                continue

            # 使用 LLM 判斷是否為法規
            prompt = f"""
請分析以下搜尋結果，判斷是否為正式的法規、指引或監管規定。

標題: {title}
網址: {url}
摘要: {snippet}
來源機構: {source_info.get('name', '')}
國家: {country_code}

如果這是一個法規/指引/規定，請提取以下資訊並以 JSON 格式回覆：
{{
    "is_regulation": true/false,
    "name": "法規原文名稱",
    "name_en": "英文名稱（如有）",
    "name_zh": "中文名稱（如有）",
    "regulation_type": "法律/規則/指引/辦法/標準",
    "topic": "cybersecurity/privacy/it_governance/operational_resilience",
    "summary": "簡短描述（50字內）"
}}

如果不是法規，回覆：{{"is_regulation": false}}
"""

            try:
                llm_response = self.llm_function(f"標題: {title}\n摘要: {snippet}", prompt)

                # 解析 JSON
                json_match = re.search(r'\{[^{}]*\}', llm_response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())

                    if data.get("is_regulation"):
                        reg = DiscoveredRegulation(
                            name=data.get("name", title),
                            name_en=data.get("name_en"),
                            name_zh=data.get("name_zh"),
                            country_code=country_code,
                            industry_code=source_info.get("industries", ["finance_general"])[0],
                            topic_code=data.get("topic", "cybersecurity"),
                            regulation_type=data.get("regulation_type"),
                            issuing_authority=source_info.get("name"),
                            official_url=url,
                            summary=data.get("summary"),
                            applicable_industries=source_info.get("industries", ["finance_general"]),
                            confidence_score=0.6,
                            source_query=result.get("query", ""),
                        )
                        discovered.append(reg)

            except Exception as e:
                self._report(f"  ⚠️ 解析失敗: {str(e)[:30]}")
                continue

        return discovered

    def discover_by_search(
        self,
        country_code: str = None,
        max_queries_per_source: int = 2,
        delay_seconds: float = 1.0,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        使用搜尋引擎發現新法規

        Args:
            country_code: 指定國家（None = 全部）
            max_queries_per_source: 每個來源最多執行幾個查詢
            delay_seconds: 查詢間隔
            verbose: 是否顯示詳細進度

        Returns:
            發現結果摘要
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": 0,
            "total_discovered": 0,
            "new_regulations": 0,
            "existing_regulations": 0,
            "added_regulations": [],
            "skipped_regulations": [],
            "errors": [],
        }

        # 決定要搜尋的國家
        countries = [country_code] if country_code else list(REGULATORY_SOURCES.keys())

        if verbose:
            self._report(f"開始搜尋 {len(countries)} 個國家/地區的法規...")
            self._report("=" * 60)

        for cc in countries:
            sources = REGULATORY_SOURCES.get(cc, [])

            if verbose:
                self._report(f"\n[{cc}] 搜尋 {len(sources)} 個監管機構...")

            for source in sources:
                source_name = source.get("name", "Unknown")
                queries = source.get("search_queries", [])[:max_queries_per_source]

                if verbose:
                    self._report(f"  📍 {source_name}")

                for query in queries:
                    results["total_queries"] += 1

                    if verbose:
                        self._report(f"    🔍 搜尋: {query[:40]}...")

                    try:
                        # 執行搜尋
                        search_result = self.search_function(query, num_results=5)
                        data = json.loads(search_result) if isinstance(search_result, str) else search_result

                        if data.get("status") == "success":
                            search_results = data.get("results", [])

                            # 為每個結果加入查詢資訊
                            for r in search_results:
                                r["query"] = query

                            # 解析結果
                            discovered = self._parse_search_results(
                                search_results, cc, source
                            )

                            for reg in discovered:
                                results["total_discovered"] += 1

                                # 檢查是否已存在
                                if self._is_regulation_exists(reg.name, cc):
                                    results["existing_regulations"] += 1
                                    results["skipped_regulations"].append({
                                        "name": reg.name,
                                        "country": cc,
                                        "reason": "已存在",
                                    })
                                    if verbose:
                                        self._report(f"      ⏭️ 已存在: {reg.name[:30]}...")
                                else:
                                    # 新增到資料庫
                                    try:
                                        self._add_regulation(reg)
                                        results["new_regulations"] += 1
                                        results["added_regulations"].append({
                                            "name": reg.name,
                                            "country": cc,
                                            "url": reg.official_url,
                                        })
                                        if verbose:
                                            self._report(f"      ✅ 新增: {reg.name[:30]}...")
                                    except Exception as e:
                                        results["errors"].append({
                                            "name": reg.name,
                                            "error": str(e),
                                        })
                                        if verbose:
                                            self._report(f"      ❌ 新增失敗: {str(e)[:30]}")

                        else:
                            results["errors"].append({
                                "query": query,
                                "error": data.get("error", "搜尋失敗"),
                            })

                    except Exception as e:
                        results["errors"].append({
                            "query": query,
                            "error": str(e),
                        })
                        if verbose:
                            self._report(f"      ❌ 錯誤: {str(e)[:30]}")

                    # 延遲避免限流
                    time.sleep(delay_seconds)

        # 顯示摘要
        if verbose:
            self._report("\n" + "=" * 60)
            self._report("發現完成！")
            self._report(f"  總查詢數: {results['total_queries']}")
            self._report(f"  發現法規: {results['total_discovered']}")
            self._report(f"  新增法規: {results['new_regulations']}")
            self._report(f"  已存在: {results['existing_regulations']}")
            self._report(f"  錯誤: {len(results['errors'])}")

        return results

    def _add_regulation(self, reg: DiscoveredRegulation):
        """將發現的法規新增到資料庫"""
        session = get_session()

        new_reg = RegulationBaseline(
            name=reg.name,
            name_en=reg.name_en,
            name_zh=reg.name_zh,
            country_code=reg.country_code,
            industry_code=reg.industry_code,
            topic_code=reg.topic_code,
            regulation_type=reg.regulation_type,
            issuing_authority=reg.issuing_authority,
            official_url=reg.official_url,
            search_keywords=reg.search_keywords,
            applicable_industries=reg.applicable_industries,
            is_cross_industry=False,
            confidence_score=reg.confidence_score,
            is_verified=False,
            is_active=True,
            is_mandatory=False,
            source="discovery",
        )

        session.add(new_reg)
        session.commit()
        session.close()

    def discover_from_url(
        self,
        url: str,
        country_code: str,
        industry_code: str = "finance_general",
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        從指定 URL 爬取並發現法規

        Args:
            url: 要爬取的網址
            country_code: 國家代碼
            industry_code: 產業代碼
            verbose: 是否顯示詳細進度

        Returns:
            發現結果
        """
        results = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "discovered": [],
            "added": [],
            "errors": [],
        }

        if verbose:
            self._report(f"爬取網頁: {url[:50]}...")

        try:
            # 爬取網頁
            fetch_result = self.fetch_function(url)
            data = json.loads(fetch_result) if isinstance(fetch_result, str) else fetch_result

            if data.get("status") != "success":
                results["errors"].append(data.get("error", "爬取失敗"))
                return results

            content = data.get("content", "")

            if not content:
                results["errors"].append("網頁內容為空")
                return results

            # 使用 LLM 解析內容
            prompt = f"""
請分析以下網頁內容，提取所有提到的法規、指引、規定。

國家: {country_code}
產業: {industry_code}

請以 JSON 陣列格式回覆，每個法規包含：
[
    {{
        "name": "法規名稱",
        "name_en": "英文名稱（如有）",
        "name_zh": "中文名稱（如有）",
        "regulation_type": "法律/規則/指引/辦法",
        "topic": "cybersecurity/privacy/it_governance",
        "summary": "簡短描述"
    }}
]

如果沒有找到法規，回覆空陣列 []
"""

            llm_response = self.llm_function(content[:10000], prompt)

            # 解析 JSON
            json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
            if json_match:
                regulations = json.loads(json_match.group())

                for reg_data in regulations:
                    reg = DiscoveredRegulation(
                        name=reg_data.get("name", ""),
                        name_en=reg_data.get("name_en"),
                        name_zh=reg_data.get("name_zh"),
                        country_code=country_code,
                        industry_code=industry_code,
                        topic_code=reg_data.get("topic", "cybersecurity"),
                        regulation_type=reg_data.get("regulation_type"),
                        official_url=url,
                        summary=reg_data.get("summary"),
                        confidence_score=0.5,
                    )

                    results["discovered"].append(reg.name)

                    if not self._is_regulation_exists(reg.name, country_code):
                        self._add_regulation(reg)
                        results["added"].append(reg.name)
                        if verbose:
                            self._report(f"  ✅ 新增: {reg.name[:40]}...")
                    else:
                        if verbose:
                            self._report(f"  ⏭️ 已存在: {reg.name[:40]}...")

        except Exception as e:
            results["errors"].append(str(e))
            if verbose:
                self._report(f"  ❌ 錯誤: {str(e)[:50]}")

        return results

    def close(self):
        """關閉資源"""
        self.manager.close()


# === 便捷函數 ===

def run_discovery(
    country_code: str = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    執行法規發現任務

    Args:
        country_code: 指定國家（None = 全部）
        verbose: 是否顯示詳細進度

    Returns:
        發現結果摘要
    """
    discoverer = RegulationDiscoverer()
    try:
        result = discoverer.discover_by_search(
            country_code=country_code,
            verbose=verbose,
        )
        return result
    finally:
        discoverer.close()


def run_discovery_for_country(country_code: str, verbose: bool = True) -> Dict[str, Any]:
    """
    執行特定國家的法規發現

    Args:
        country_code: 國家代碼
        verbose: 是否顯示詳細進度

    Returns:
        發現結果摘要
    """
    return run_discovery(country_code=country_code, verbose=verbose)


if __name__ == "__main__":
    # 測試發現功能
    print("執行法規發現測試（僅台灣）...")
    result = run_discovery(country_code="TW", verbose=True)
    print(f"\n結果摘要:")
    print(f"  新增: {result['new_regulations']} 筆")
    print(f"  已存在: {result['existing_regulations']} 筆")
