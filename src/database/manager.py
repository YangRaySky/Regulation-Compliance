"""
資料庫管理工具

提供:
- CRUD 操作
- 信心度計算
- 驗證機制
- 查詢功能
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from .models import (
    Country,
    Industry,
    Topic,
    RegulationBaseline,
    VerificationLog,
    get_session,
)


class BaselineManager:
    """法規 Baseline 管理器"""

    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()

    def close(self):
        """關閉 session"""
        self.session.close()

    # ============================================================
    # 國家/產業/主題 查詢
    # ============================================================

    def get_all_countries(self) -> list[dict]:
        """取得所有國家"""
        countries = self.session.query(Country).filter_by(is_active=True).all()
        return [
            {
                "code": c.code,
                "name_zh": c.name_zh,
                "name_en": c.name_en,
                "region": c.region,
            }
            for c in countries
        ]

    def get_all_industries(self) -> list[dict]:
        """取得所有產業"""
        industries = self.session.query(Industry).filter_by(is_active=True).all()
        return [
            {
                "code": i.code,
                "name_zh": i.name_zh,
                "name_en": i.name_en,
                "category": i.category,
            }
            for i in industries
        ]

    def get_all_topics(self) -> list[dict]:
        """取得所有主題"""
        topics = self.session.query(Topic).filter_by(is_active=True).all()
        return [
            {
                "code": t.code,
                "name_zh": t.name_zh,
                "name_en": t.name_en,
            }
            for t in topics
        ]

    def get_country_by_name(self, name: str) -> Optional[Country]:
        """根據名稱取得國家（支援中英文）"""
        return self.session.query(Country).filter(
            or_(
                Country.name_zh == name,
                Country.name_en == name,
                Country.code == name.upper(),
            )
        ).first()

    def get_industry_by_name(self, name: str) -> Optional[Industry]:
        """根據名稱取得產業（支援中英文）"""
        return self.session.query(Industry).filter(
            or_(
                Industry.name_zh.contains(name),
                Industry.name_en.ilike(f"%{name}%"),
                Industry.code == name,
            )
        ).first()

    # ============================================================
    # 法規 Baseline CRUD
    # ============================================================

    def add_regulation(
        self,
        name: str,
        country_code: str,
        industry_code: str,
        topic_code: str,
        name_en: str = None,
        name_zh: str = None,
        regulation_type: str = None,
        issuing_authority: str = None,
        official_url: str = None,
        search_keywords: list[str] = None,
        is_mandatory: bool = False,
        source: str = "manual",
    ) -> RegulationBaseline:
        """新增法規"""

        # 檢查是否已存在
        existing = self.session.query(RegulationBaseline).filter(
            and_(
                RegulationBaseline.name == name,
                RegulationBaseline.country_code == country_code,
                RegulationBaseline.industry_code == industry_code,
            )
        ).first()

        if existing:
            print(f"[Manager] 法規已存在: {name}")
            return existing

        regulation = RegulationBaseline(
            name=name,
            name_en=name_en,
            name_zh=name_zh,
            country_code=country_code,
            industry_code=industry_code,
            topic_code=topic_code,
            regulation_type=regulation_type,
            issuing_authority=issuing_authority,
            official_url=official_url,
            search_keywords=search_keywords or [name],
            is_mandatory=is_mandatory,
            source=source,
            confidence_score=0.5 if source == "manual" else 0.3,
            is_verified=source == "manual",
        )

        self.session.add(regulation)
        self.session.commit()
        print(f"[Manager] 已新增法規: {name}")
        return regulation

    def update_regulation(self, regulation_id: int, **kwargs) -> Optional[RegulationBaseline]:
        """更新法規"""
        regulation = self.session.query(RegulationBaseline).get(regulation_id)
        if not regulation:
            return None

        for key, value in kwargs.items():
            if hasattr(regulation, key):
                setattr(regulation, key, value)

        regulation.updated_at = datetime.utcnow()
        self.session.commit()
        return regulation

    def delete_regulation(self, regulation_id: int) -> bool:
        """刪除法規（軟刪除）"""
        regulation = self.session.query(RegulationBaseline).get(regulation_id)
        if not regulation:
            return False

        regulation.is_active = False
        regulation.updated_at = datetime.utcnow()
        self.session.commit()
        return True

    def get_regulation(self, regulation_id: int) -> Optional[RegulationBaseline]:
        """取得單一法規"""
        return self.session.query(RegulationBaseline).get(regulation_id)

    # ============================================================
    # 查詢功能
    # ============================================================

    def get_regulations_by_query(
        self,
        country_code: str = None,
        industry_code: str = None,
        topic_code: str = None,
        is_mandatory: bool = None,
        min_confidence: float = None,
        is_verified: bool = None,
    ) -> list[RegulationBaseline]:
        """根據條件查詢法規"""

        query = self.session.query(RegulationBaseline).filter(
            RegulationBaseline.is_active == True
        )

        if country_code:
            query = query.filter(RegulationBaseline.country_code == country_code)
        if industry_code:
            query = query.filter(RegulationBaseline.industry_code == industry_code)
        if topic_code:
            query = query.filter(RegulationBaseline.topic_code == topic_code)
        if is_mandatory is not None:
            query = query.filter(RegulationBaseline.is_mandatory == is_mandatory)
        if min_confidence is not None:
            query = query.filter(RegulationBaseline.confidence_score >= min_confidence)
        if is_verified is not None:
            query = query.filter(RegulationBaseline.is_verified == is_verified)

        return query.order_by(
            RegulationBaseline.is_mandatory.desc(),
            RegulationBaseline.confidence_score.desc(),
        ).all()

    def get_mandatory_regulations(
        self,
        country_code: str,
        industry_code: str = None,
        topic_code: str = None,
    ) -> list[RegulationBaseline]:
        """取得必搜法規清單"""
        return self.get_regulations_by_query(
            country_code=country_code,
            industry_code=industry_code,
            topic_code=topic_code,
            is_mandatory=True,
        )

    def get_search_keywords(
        self,
        country_code: str,
        industry_code: str = None,
        topic_code: str = None,
    ) -> list[dict]:
        """取得搜尋關鍵字清單（供 Researcher Agent 使用）"""

        regulations = self.get_mandatory_regulations(
            country_code=country_code,
            industry_code=industry_code,
            topic_code=topic_code,
        )

        keywords = []
        for reg in regulations:
            if reg.search_keywords:
                for kw in reg.search_keywords:
                    keywords.append({
                        "keyword": kw,
                        "regulation_name": reg.name,
                        "regulation_id": reg.id,
                        "priority": reg.search_priority or 1,
                    })

        return sorted(keywords, key=lambda x: x["priority"])

    # ============================================================
    # 信心度計算
    # ============================================================

    def calculate_confidence(self, regulation: RegulationBaseline) -> float:
        """
        計算法規信心度

        信心度因子:
        - 人工驗證過: +0.3
        - 有官方 URL 且可存取: +0.2
        - 最近 30 天內搜尋到: +0.2
        - 多次搜尋都有出現 (found_count > 3): +0.2
        - 來自官方網站 (.gov): +0.1
        ---
        - 超過 90 天未搜尋到: -0.3
        - URL 失效: -0.2
        - 標記為草案/已廢止: -0.5
        """

        score = 0.0

        # 正向因子
        if regulation.is_verified:
            score += 0.3

        if regulation.official_url:
            if any(gov in regulation.official_url for gov in [".gov", ".go.", ".gob"]):
                score += 0.3  # 官方 URL
            else:
                score += 0.1

        if regulation.last_found_at:
            days_since_found = (datetime.utcnow() - regulation.last_found_at).days
            if days_since_found <= 30:
                score += 0.2
            elif days_since_found <= 90:
                score += 0.1

        if regulation.found_count and regulation.found_count >= 3:
            score += 0.2

        # 負向因子
        if regulation.last_found_at:
            days_since_found = (datetime.utcnow() - regulation.last_found_at).days
            if days_since_found > 90:
                score -= 0.3

        if regulation.not_found_count and regulation.not_found_count >= 3:
            score -= 0.2

        # 確保在 0-1 範圍
        return max(0.0, min(1.0, score))

    def update_confidence(self, regulation_id: int) -> float:
        """更新法規信心度"""
        regulation = self.session.query(RegulationBaseline).get(regulation_id)
        if not regulation:
            return 0.0

        new_confidence = self.calculate_confidence(regulation)
        regulation.confidence_score = new_confidence
        regulation.updated_at = datetime.utcnow()
        self.session.commit()

        return new_confidence

    # ============================================================
    # 驗證記錄
    # ============================================================

    def record_verification(
        self,
        regulation_id: int,
        was_found: bool,
        verification_type: str = "search",
        search_query: str = None,
        search_results_count: int = None,
        url_accessible: bool = None,
        notes: str = None,
        verified_by: str = "system",
    ) -> VerificationLog:
        """記錄驗證結果"""

        regulation = self.session.query(RegulationBaseline).get(regulation_id)
        if not regulation:
            raise ValueError(f"找不到法規 ID: {regulation_id}")

        old_confidence = regulation.confidence_score

        # 更新法規記錄
        if was_found:
            regulation.last_found_at = datetime.utcnow()
            regulation.found_count = (regulation.found_count or 0) + 1
        else:
            regulation.not_found_count = (regulation.not_found_count or 0) + 1

        regulation.last_verified_at = datetime.utcnow()

        # 重新計算信心度
        new_confidence = self.calculate_confidence(regulation)
        regulation.confidence_score = new_confidence

        # 建立驗證記錄
        log = VerificationLog(
            regulation_id=regulation_id,
            verification_type=verification_type,
            was_found=was_found,
            search_query=search_query,
            search_results_count=search_results_count,
            url_accessible=url_accessible,
            old_confidence=old_confidence,
            new_confidence=new_confidence,
            notes=notes,
            verified_by=verified_by,
        )

        self.session.add(log)
        self.session.commit()

        return log

    def get_verification_history(
        self,
        regulation_id: int,
        limit: int = 10,
    ) -> list[VerificationLog]:
        """取得驗證歷史"""
        return (
            self.session.query(VerificationLog)
            .filter_by(regulation_id=regulation_id)
            .order_by(VerificationLog.verified_at.desc())
            .limit(limit)
            .all()
        )

    # ============================================================
    # 統計功能
    # ============================================================

    def get_statistics(self) -> dict:
        """取得統計資訊"""
        total = self.session.query(RegulationBaseline).filter_by(is_active=True).count()
        verified = self.session.query(RegulationBaseline).filter_by(
            is_active=True, is_verified=True
        ).count()
        mandatory = self.session.query(RegulationBaseline).filter_by(
            is_active=True, is_mandatory=True
        ).count()

        # 按國家統計
        by_country = {}
        countries = self.session.query(Country).filter_by(is_active=True).all()
        for country in countries:
            count = self.session.query(RegulationBaseline).filter_by(
                is_active=True, country_code=country.code
            ).count()
            if count > 0:
                by_country[country.name_zh] = count

        # 按產業統計
        by_industry = {}
        industries = self.session.query(Industry).filter_by(is_active=True).all()
        for industry in industries:
            count = self.session.query(RegulationBaseline).filter_by(
                is_active=True, industry_code=industry.code
            ).count()
            if count > 0:
                by_industry[industry.name_zh] = count

        return {
            "total": total,
            "verified": verified,
            "mandatory": mandatory,
            "by_country": by_country,
            "by_industry": by_industry,
        }

    def export_to_dict(
        self,
        country_code: str = None,
        industry_code: str = None,
    ) -> list[dict]:
        """匯出法規為字典格式"""
        regulations = self.get_regulations_by_query(
            country_code=country_code,
            industry_code=industry_code,
        )

        return [
            {
                "id": r.id,
                "name": r.name,
                "name_en": r.name_en,
                "name_zh": r.name_zh,
                "country_code": r.country_code,
                "industry_code": r.industry_code,
                "topic_code": r.topic_code,
                "regulation_type": r.regulation_type,
                "issuing_authority": r.issuing_authority,
                "official_url": r.official_url,
                "search_keywords": r.search_keywords,
                "confidence_score": r.confidence_score,
                "is_verified": r.is_verified,
                "is_mandatory": r.is_mandatory,
                "last_verified_at": r.last_verified_at.isoformat() if r.last_verified_at else None,
                "last_found_at": r.last_found_at.isoformat() if r.last_found_at else None,
            }
            for r in regulations
        ]
