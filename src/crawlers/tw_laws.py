"""
台灣法規資料庫爬蟲

從全國法規資料庫 (law.moj.gov.tw) 擷取法規資料。
"""

import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseCrawler, CrawlerResult


class TaiwanLawsCrawler(BaseCrawler):
    """
    全國法規資料庫爬蟲

    網站: https://law.moj.gov.tw/
    """

    @property
    def source_name(self) -> str:
        return "全國法規資料庫"

    @property
    def base_url(self) -> str:
        return "https://law.moj.gov.tw"

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """
        搜尋法規

        Args:
            query: 搜尋關鍵字
            category: 法規類別
            limit: 結果數量上限

        Returns:
            搜尋結果列表
        """
        # 建構搜尋 URL
        search_url = f"{self.base_url}/LawClass/LawSearchContent.aspx"

        try:
            content, status_code = await self.fetch_url(
                search_url,
                params={
                    "keyword": query,
                    "page": "1",
                },
            )

            if status_code != 200:
                return []

            return self._parse_search_results(content, limit)

        except Exception as e:
            print(f"搜尋失敗: {e}")
            return []

    def _parse_search_results(
        self,
        html: str,
        limit: int,
    ) -> list[dict]:
        """解析搜尋結果頁面"""
        soup = BeautifulSoup(html, "lxml")
        results = []

        # 尋找搜尋結果表格
        table = soup.find("table", class_="law-result")
        if not table:
            # 嘗試其他選擇器
            rows = soup.find_all("tr", class_="law-item")
        else:
            rows = table.find_all("tr")

        for row in rows[:limit]:
            try:
                # 提取法規名稱與連結
                link = row.find("a")
                if not link:
                    continue

                title = link.get_text(strip=True)
                href = link.get("href", "")

                # 提取法規代碼
                pcode_match = re.search(r"pcode=([A-Z0-9]+)", href)
                pcode = pcode_match.group(1) if pcode_match else None

                results.append({
                    "title": title,
                    "pcode": pcode,
                    "url": urljoin(self.base_url, href),
                })

            except Exception:
                continue

        return results

    async def get_regulation(
        self,
        regulation_id: str,
    ) -> CrawlerResult:
        """
        取得法規完整內容

        Args:
            regulation_id: 法規代碼 (pcode)

        Returns:
            爬蟲結果
        """
        # 建構法規頁面 URL
        law_url = f"{self.base_url}/LawClass/LawAll.aspx?pcode={regulation_id}"

        try:
            content, status_code = await self.fetch_url(law_url)

            if status_code != 200:
                return CrawlerResult(
                    status="failed",
                    source_name=self.source_name,
                    source_url=law_url,
                    content="",
                    content_type="html",
                    error=f"HTTP {status_code}",
                )

            # 解析法規內容
            parsed = self._parse_law_page(content, law_url)

            return CrawlerResult(
                status="success",
                source_name=self.source_name,
                source_url=law_url,
                content=parsed["content"],
                content_type="html",
                metadata={
                    "title": parsed["title"],
                    "pcode": regulation_id,
                    "effective_date": parsed.get("effective_date"),
                    "last_amended_date": parsed.get("last_amended_date"),
                    "issuing_authority": parsed.get("issuing_authority"),
                    "articles_count": parsed.get("articles_count", 0),
                },
            )

        except Exception as e:
            return CrawlerResult(
                status="failed",
                source_name=self.source_name,
                source_url=law_url,
                content="",
                content_type="html",
                error=str(e),
            )

    def _parse_law_page(
        self,
        html: str,
        url: str,
    ) -> dict:
        """
        解析法規頁面

        Args:
            html: 頁面 HTML
            url: 頁面 URL

        Returns:
            解析後的法規資料
        """
        soup = BeautifulSoup(html, "lxml")

        result = {
            "title": "",
            "content": "",
            "effective_date": None,
            "last_amended_date": None,
            "issuing_authority": None,
            "articles_count": 0,
        }

        # 提取法規名稱
        title_elem = soup.find("h1") or soup.find("title")
        if title_elem:
            result["title"] = title_elem.get_text(strip=True)

        # 提取法規基本資訊
        info_table = soup.find("table", class_="law-info")
        if info_table:
            for row in info_table.find_all("tr"):
                cells = row.find_all(["th", "td"])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)

                    if "生效日期" in label or "施行日期" in label:
                        result["effective_date"] = value
                    elif "修正日期" in label:
                        result["last_amended_date"] = value
                    elif "發布機關" in label or "主管機關" in label:
                        result["issuing_authority"] = value

        # 提取法規條文
        articles = []
        article_divs = soup.find_all("div", class_="law-article")

        if not article_divs:
            # 嘗試其他選擇器
            article_divs = soup.find_all("div", id=re.compile(r"article"))

        for div in article_divs:
            article_text = div.get_text(strip=True)
            if article_text:
                articles.append(article_text)

        result["articles_count"] = len(articles)
        result["content"] = "\n\n".join(articles) if articles else soup.get_text()

        return result

    async def get_by_name(
        self,
        law_name: str,
    ) -> CrawlerResult:
        """
        依法規名稱取得法規

        Args:
            law_name: 法規名稱

        Returns:
            爬蟲結果
        """
        # 先搜尋法規
        results = await self.search(law_name, limit=5)

        if not results:
            return CrawlerResult(
                status="failed",
                source_name=self.source_name,
                source_url=self.base_url,
                content="",
                content_type="html",
                error=f"找不到法規: {law_name}",
            )

        # 找到最匹配的結果
        best_match = None
        for r in results:
            if law_name in r["title"]:
                best_match = r
                break

        if not best_match:
            best_match = results[0]

        # 取得法規內容
        if best_match.get("pcode"):
            return await self.get_regulation(best_match["pcode"])

        return CrawlerResult(
            status="failed",
            source_name=self.source_name,
            source_url=self.base_url,
            content="",
            content_type="html",
            error="無法取得法規代碼",
        )


# 常用台灣資安法規代碼（擴充版）
COMMON_TW_LAWS = {
    # === 核心資安法規 ===
    "個人資料保護法": "I0050021",
    "個資法": "I0050021",  # 別名
    "資通安全管理法": "A0030297",
    "資安法": "A0030297",  # 別名
    "電子簽章法": "J0080037",

    # === 個資相關細則 ===
    "個人資料保護法施行細則": "I0050022",
    "個人資料保護法之特定目的及個人資料之類別": "I0050028",

    # === 資安管理相關 ===
    "資通安全管理法施行細則": "A0030298",
    "資通安全責任等級分級辦法": "A0030299",
    "資通安全事件通報及應變辦法": "A0030300",
    "特定非公務機關資通安全維護計畫實施情形稽核辦法": "A0030301",

    # === 金融業資安 ===
    "金融機構辦理電子銀行業務安全控管作業基準": "G0380251",
    "保險業辦理電子商務應注意事項": "G0390067",
    "證券期貨業電子式交易型態資通安全管理基準": "G0400138",

    # === 電信與通訊 ===
    "電信管理法": "K0060108",
    "電信事業個人資料檔案安全維護計畫及處理辦法": "K0060127",

    # === 其他相關法規 ===
    "刑法": "C0000001",
    "政府資訊公開法": "I0020026",
    "行政程序法": "A0030055",
    "營業秘密法": "J0080028",
    "公平交易法": "J0150002",

    # === 醫療資安 ===
    "醫療機構電子病歷製作及管理辦法": "L0020121",

    # === 關鍵基礎設施 ===
    "國家資通安全發展方案": "A0030302",  # 行政院核定
}

# 法規類別索引（便於分類搜尋）
TW_LAW_CATEGORIES = {
    "個資": ["個人資料保護法", "個人資料保護法施行細則", "個人資料保護法之特定目的及個人資料之類別"],
    "資安": ["資通安全管理法", "資通安全管理法施行細則", "資通安全責任等級分級辦法", "資通安全事件通報及應變辦法"],
    "金融": [
        "金融機構辦理電子銀行業務安全控管作業基準",
        "保險業辦理電子商務應注意事項",
        "證券期貨業電子式交易型態資通安全管理基準",
    ],
    "電信": ["電信管理法", "電信事業個人資料檔案安全維護計畫及處理辦法"],
    "醫療": ["醫療機構電子病歷製作及管理辦法"],
}


async def fetch_tw_law(law_name: str) -> CrawlerResult:
    """
    取得台灣法規的便捷函數

    Args:
        law_name: 法規名稱

    Returns:
        爬蟲結果
    """
    async with TaiwanLawsCrawler() as crawler:
        # 檢查是否有預設的法規代碼
        if law_name in COMMON_TW_LAWS:
            return await crawler.get_regulation(COMMON_TW_LAWS[law_name])

        return await crawler.get_by_name(law_name)
