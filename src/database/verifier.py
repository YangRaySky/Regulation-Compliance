"""
法規定期驗證模組

提供:
- 定期驗證排程
- 批次驗證功能
- 信心度自動更新
- 驗證報告生成
"""

import json
import time
from datetime import datetime, timedelta
from typing import Optional, Callable

from .manager import BaselineManager
from .models import RegulationBaseline, VerificationLog, get_session


class RegulationVerifier:
    """法規驗證器"""

    def __init__(
        self,
        search_function: Optional[Callable] = None,
        status_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        初始化驗證器

        Args:
            search_function: 搜尋函數 (預設使用 web_search)
            status_callback: 狀態回調函數
        """
        self.manager = BaselineManager()
        self.status_callback = status_callback or (lambda x: print(x))

        # 預設使用 web_search
        if search_function is None:
            from ..agents.tools import web_search
            self.search_function = web_search
        else:
            self.search_function = search_function

    def _report(self, message: str):
        """報告狀態"""
        self.status_callback(message)

    def verify_single(
        self,
        regulation: RegulationBaseline,
        verbose: bool = False,
    ) -> dict:
        """
        驗證單一法規

        Returns:
            驗證結果字典
        """
        result = {
            "regulation_id": regulation.id,
            "regulation_name": regulation.name,
            "country_code": regulation.country_code,
            "was_found": False,
            "search_results_count": 0,
            "top_result": None,
            "old_confidence": regulation.confidence_score,
            "new_confidence": 0.0,
            "error": None,
        }

        # 取得搜尋關鍵字
        keywords = regulation.search_keywords or [regulation.name]
        keyword = keywords[0]

        if verbose:
            self._report(f"[{regulation.country_code}] 驗證: {regulation.name[:40]}...")

        try:
            # 執行搜尋
            search_result = self.search_function(keyword, num_results=3)
            data = json.loads(search_result) if isinstance(search_result, str) else search_result

            if data.get("status") == "success":
                results = data.get("results", [])
                result["search_results_count"] = len(results)

                if results:
                    result["was_found"] = True
                    result["top_result"] = {
                        "title": results[0].get("title", "")[:100],
                        "url": results[0].get("url", ""),
                    }
                    if verbose:
                        self._report(f"  ✅ 找到 {len(results)} 筆結果")
                else:
                    if verbose:
                        self._report(f"  ⚠️ 搜尋成功但無結果")
            else:
                result["error"] = data.get("error", "搜尋失敗")
                if verbose:
                    self._report(f"  ❌ {result['error']}")

        except Exception as e:
            result["error"] = str(e)
            if verbose:
                self._report(f"  ❌ 錯誤: {str(e)[:50]}")

        # 記錄驗證結果並更新信心度
        try:
            log = self.manager.record_verification(
                regulation_id=regulation.id,
                was_found=result["was_found"],
                verification_type="scheduled",
                search_query=keyword,
                search_results_count=result["search_results_count"],
                notes=json.dumps(result["top_result"], ensure_ascii=False) if result["top_result"] else None,
                verified_by="system",
            )
            result["new_confidence"] = log.new_confidence
        except Exception as e:
            result["error"] = f"記錄失敗: {str(e)}"

        return result

    def verify_batch(
        self,
        country_code: str = None,
        industry_code: str = None,
        topic_code: str = None,
        only_mandatory: bool = False,
        max_count: int = None,
        delay_seconds: float = 0.5,
        verbose: bool = True,
    ) -> dict:
        """
        批次驗證法規

        Args:
            country_code: 篩選國家
            industry_code: 篩選產業
            topic_code: 篩選主題
            only_mandatory: 只驗證必搜法規
            max_count: 最大驗證數量
            delay_seconds: 每次搜尋間隔（避免 API 限流）
            verbose: 是否顯示詳細進度

        Returns:
            批次驗證結果摘要
        """
        # 取得待驗證法規
        regulations = self.manager.get_regulations_by_query(
            country_code=country_code,
            industry_code=industry_code,
            topic_code=topic_code,
            is_mandatory=True if only_mandatory else None,
        )

        if max_count:
            regulations = regulations[:max_count]

        total = len(regulations)
        if verbose:
            self._report(f"開始驗證 {total} 筆法規...")
            self._report("=" * 60)

        # 驗證結果統計
        results = {
            "total": total,
            "verified": 0,
            "found": 0,
            "not_found": 0,
            "errors": 0,
            "details": [],
            "by_country": {},
            "timestamp": datetime.now().isoformat(),
        }

        for i, reg in enumerate(regulations):
            # 驗證單一法規
            result = self.verify_single(reg, verbose=verbose)
            results["details"].append(result)
            results["verified"] += 1

            # 統計
            if result["error"]:
                results["errors"] += 1
            elif result["was_found"]:
                results["found"] += 1
            else:
                results["not_found"] += 1

            # 按國家統計
            cc = reg.country_code
            if cc not in results["by_country"]:
                results["by_country"][cc] = {"total": 0, "found": 0, "not_found": 0}
            results["by_country"][cc]["total"] += 1
            if result["was_found"]:
                results["by_country"][cc]["found"] += 1
            else:
                results["by_country"][cc]["not_found"] += 1

            # 延遲避免限流
            if i < total - 1 and delay_seconds > 0:
                time.sleep(delay_seconds)

        # 顯示摘要
        if verbose:
            self._report("=" * 60)
            self._report(f"驗證完成！")
            self._report(f"  總數: {results['total']}")
            self._report(f"  找到: {results['found']} ({results['found']/max(1,results['total'])*100:.1f}%)")
            self._report(f"  未找到: {results['not_found']}")
            self._report(f"  錯誤: {results['errors']}")

        return results

    def verify_stale(
        self,
        days_threshold: int = 30,
        max_count: int = 50,
        verbose: bool = True,
    ) -> dict:
        """
        驗證過期的法規（超過指定天數未驗證）

        Args:
            days_threshold: 過期天數閾值
            max_count: 最大驗證數量
            verbose: 是否顯示詳細進度

        Returns:
            驗證結果摘要
        """
        session = get_session()

        # 找出需要重新驗證的法規
        threshold_date = datetime.utcnow() - timedelta(days=days_threshold)
        stale_regulations = (
            session.query(RegulationBaseline)
            .filter(RegulationBaseline.is_active == True)
            .filter(
                (RegulationBaseline.last_verified_at == None) |
                (RegulationBaseline.last_verified_at < threshold_date)
            )
            .order_by(RegulationBaseline.is_mandatory.desc())
            .limit(max_count)
            .all()
        )

        session.close()

        if verbose:
            self._report(f"找到 {len(stale_regulations)} 筆需要重新驗證的法規")

        # 批次驗證
        total = len(stale_regulations)
        results = {
            "total": total,
            "verified": 0,
            "found": 0,
            "not_found": 0,
            "errors": 0,
            "details": [],
            "timestamp": datetime.now().isoformat(),
        }

        for i, reg in enumerate(stale_regulations):
            result = self.verify_single(reg, verbose=verbose)
            results["details"].append(result)
            results["verified"] += 1

            if result["error"]:
                results["errors"] += 1
            elif result["was_found"]:
                results["found"] += 1
            else:
                results["not_found"] += 1

            if i < total - 1:
                time.sleep(0.5)

        return results

    def generate_report(self) -> dict:
        """
        生成驗證報告

        Returns:
            完整驗證報告
        """
        stats = self.manager.get_statistics()
        session = get_session()

        # 取得最近驗證記錄
        recent_logs = (
            session.query(VerificationLog)
            .order_by(VerificationLog.verified_at.desc())
            .limit(100)
            .all()
        )

        # 統計最近驗證結果
        recent_found = sum(1 for log in recent_logs if log.was_found)
        recent_not_found = sum(1 for log in recent_logs if not log.was_found)

        # 取得低信心度法規
        low_confidence = (
            session.query(RegulationBaseline)
            .filter(RegulationBaseline.is_active == True)
            .filter(RegulationBaseline.confidence_score < 0.5)
            .order_by(RegulationBaseline.confidence_score)
            .limit(20)
            .all()
        )

        # 取得未驗證法規
        never_verified = (
            session.query(RegulationBaseline)
            .filter(RegulationBaseline.is_active == True)
            .filter(RegulationBaseline.last_verified_at == None)
            .count()
        )

        session.close()

        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_regulations": stats["total"],
                "verified_regulations": stats["verified"],
                "mandatory_regulations": stats["mandatory"],
                "never_verified": never_verified,
            },
            "recent_verification": {
                "total_checks": len(recent_logs),
                "found": recent_found,
                "not_found": recent_not_found,
                "success_rate": recent_found / max(1, len(recent_logs)) * 100,
            },
            "low_confidence_regulations": [
                {
                    "id": reg.id,
                    "name": reg.name[:50],
                    "country": reg.country_code,
                    "confidence": reg.confidence_score,
                }
                for reg in low_confidence
            ],
            "by_country": stats["by_country"],
            "by_industry": stats["by_industry"],
        }

        return report

    def close(self):
        """關閉資源"""
        self.manager.close()


# === 便捷函數 ===

def run_scheduled_verification(
    days_threshold: int = 30,
    max_count: int = 50,
    verbose: bool = True,
) -> dict:
    """
    執行定期驗證任務

    這個函數可以被 cron job 或排程器呼叫

    Args:
        days_threshold: 過期天數閾值
        max_count: 最大驗證數量
        verbose: 是否顯示詳細進度

    Returns:
        驗證結果摘要
    """
    verifier = RegulationVerifier()
    try:
        result = verifier.verify_stale(
            days_threshold=days_threshold,
            max_count=max_count,
            verbose=verbose,
        )
        return result
    finally:
        verifier.close()


def run_full_verification(
    country_code: str = None,
    only_mandatory: bool = True,
    verbose: bool = True,
) -> dict:
    """
    執行完整驗證

    Args:
        country_code: 指定國家（None = 全部）
        only_mandatory: 只驗證必搜法規
        verbose: 是否顯示詳細進度

    Returns:
        驗證結果摘要
    """
    verifier = RegulationVerifier()
    try:
        result = verifier.verify_batch(
            country_code=country_code,
            only_mandatory=only_mandatory,
            verbose=verbose,
        )
        return result
    finally:
        verifier.close()


if __name__ == "__main__":
    # 測試驗證功能
    print("執行定期驗證測試...")
    result = run_scheduled_verification(max_count=5, verbose=True)
    print(f"\n結果: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")
