"""
匯入必搜法規清單到資料庫

這些是各國金融業資安的核心法規，用於確保搜尋穩定性
"""

from .manager import BaselineManager

# ============================================================
# 日本金融業資安法規
# ============================================================

JAPAN_REGULATIONS = [
    {
        "name": "サイバーセキュリティ基本法",
        "name_en": "Basic Act on Cybersecurity",
        "name_zh": "網路安全基本法",
        "regulation_type": "法律",
        "issuing_authority": "内閣",
        "search_keywords": ["サイバーセキュリティ基本法", "Japan Basic Act Cybersecurity"],
    },
    {
        "name": "金融分野におけるサイバーセキュリティに関するガイドライン",
        "name_en": "Guidelines for Cybersecurity in the Financial Sector",
        "name_zh": "金融領域網路安全指引",
        "regulation_type": "指引",
        "issuing_authority": "金融庁",
        "search_keywords": ["金融分野 サイバーセキュリティ ガイドライン", "FSA cybersecurity guidelines"],
    },
    {
        "name": "主要行等向けの総合的な監督指針",
        "name_en": "Comprehensive Guidelines for Supervision of Major Banks",
        "name_zh": "主要銀行綜合監督指針",
        "regulation_type": "指針",
        "issuing_authority": "金融庁",
        "search_keywords": ["主要行 監督指針", "金融庁 主要行 監督"],
    },
    {
        "name": "金融商品取引業者等向けの総合的な監督指針",
        "name_en": "Comprehensive Guidelines for Supervision of Securities Companies",
        "name_zh": "證券業監督指針",
        "regulation_type": "指針",
        "issuing_authority": "金融庁",
        "search_keywords": ["金融商品取引業者 監督指針", "証券会社 監督指針"],
    },
    {
        "name": "保険会社向けの総合的な監督指針",
        "name_en": "Comprehensive Guidelines for Supervision of Insurance Companies",
        "name_zh": "保險公司監督指針",
        "regulation_type": "指針",
        "issuing_authority": "金融庁",
        "search_keywords": ["保険会社 監督指針", "金融庁 保険 監督"],
    },
    {
        "name": "個人情報の保護に関する法律",
        "name_en": "Act on the Protection of Personal Information",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "個人情報保護委員会",
        "search_keywords": ["個人情報保護法", "Japan APPI personal information"],
    },
]


# ============================================================
# 新加坡金融業資安法規
# ============================================================

SINGAPORE_REGULATIONS = [
    {
        "name": "Technology Risk Management Guidelines",
        "name_en": "Technology Risk Management Guidelines",
        "name_zh": "技術風險管理指引",
        "regulation_type": "指引",
        "issuing_authority": "MAS",
        "official_url": "https://www.mas.gov.sg/regulation/guidelines/technology-risk-management-guidelines",
        "search_keywords": ["MAS Technology Risk Management Guidelines", "MAS TRM"],
    },
    {
        "name": "Guidelines on Outsourcing",
        "name_en": "Guidelines on Outsourcing",
        "name_zh": "委外管理指引",
        "regulation_type": "指引",
        "issuing_authority": "MAS",
        "search_keywords": ["MAS outsourcing guidelines", "MAS Guidelines on Outsourcing"],
    },
    {
        "name": "Notice on Cyber Hygiene",
        "name_en": "Notice on Cyber Hygiene",
        "name_zh": "網路衛生通告",
        "regulation_type": "通告",
        "issuing_authority": "MAS",
        "search_keywords": ["MAS cyber hygiene notice", "MAS Notice PSN01"],
    },
    {
        "name": "Cybersecurity Act 2018",
        "name_en": "Cybersecurity Act 2018",
        "name_zh": "網路安全法",
        "regulation_type": "法律",
        "issuing_authority": "Singapore Government",
        "search_keywords": ["Singapore Cybersecurity Act", "Cybersecurity Act 2018"],
    },
    {
        "name": "Personal Data Protection Act",
        "name_en": "Personal Data Protection Act",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "PDPC",
        "search_keywords": ["PDPA Singapore", "Singapore Personal Data Protection Act"],
    },
    {
        "name": "Payment Services Act",
        "name_en": "Payment Services Act",
        "name_zh": "支付服務法",
        "regulation_type": "法律",
        "issuing_authority": "MAS",
        "search_keywords": ["Payment Services Act Singapore", "MAS Payment Services Act"],
    },
]


# ============================================================
# 韓國金融業資安法規
# ============================================================

KOREA_REGULATIONS = [
    {
        "name": "전자금융거래법",
        "name_en": "Electronic Financial Transactions Act",
        "name_zh": "電子金融交易法",
        "regulation_type": "法律",
        "issuing_authority": "금융위원회 (FSC)",
        "search_keywords": ["전자금융거래법", "Korea Electronic Financial Transactions Act"],
    },
    {
        "name": "전자금융감독규정",
        "name_en": "Electronic Financial Supervision Regulations",
        "name_zh": "電子金融監督規定",
        "regulation_type": "規定",
        "issuing_authority": "금융감독원 (FSS)",
        "search_keywords": ["전자금융감독규정", "Korea electronic financial supervision"],
    },
    {
        "name": "신용정보의 이용 및 보호에 관한 법률",
        "name_en": "Credit Information Act",
        "name_zh": "信用情報法",
        "regulation_type": "法律",
        "issuing_authority": "금융위원회 (FSC)",
        "search_keywords": ["신용정보법", "Korea Credit Information Act"],
    },
    {
        "name": "개인정보 보호법",
        "name_en": "Personal Information Protection Act",
        "name_zh": "個人資訊保護法",
        "regulation_type": "法律",
        "issuing_authority": "개인정보보호위원회",
        "search_keywords": ["개인정보보호법", "Korea PIPA personal information"],
    },
]


# ============================================================
# 台灣金融業資安法規
# ============================================================

TAIWAN_REGULATIONS = [
    {
        "name": "資通安全管理法",
        "name_en": "Cyber Security Management Act",
        "name_zh": "資通安全管理法",
        "regulation_type": "法律",
        "issuing_authority": "數位發展部",
        "search_keywords": ["資通安全管理法", "Taiwan Cyber Security Management Act"],
    },
    {
        "name": "個人資料保護法",
        "name_en": "Personal Data Protection Act",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "法務部",
        "search_keywords": ["個人資料保護法", "Taiwan Personal Data Protection Act"],
    },
    {
        "name": "金融資安行動方案",
        "name_en": "Financial Cybersecurity Action Plan",
        "name_zh": "金融資安行動方案",
        "regulation_type": "方案",
        "issuing_authority": "金管會",
        "search_keywords": ["金融資安行動方案", "金管會 資安"],
    },
    {
        "name": "金融機構辦理電腦系統資訊安全評估辦法",
        "name_en": "Regulations Governing Information Security Assessment of Financial Institutions",
        "name_zh": "金融機構辦理電腦系統資訊安全評估辦法",
        "regulation_type": "辦法",
        "issuing_authority": "金管會",
        "search_keywords": ["金融機構 資訊安全評估", "金管會 資安評估"],
    },
]


# ============================================================
# 德國金融業資安法規
# ============================================================

GERMANY_REGULATIONS = [
    {
        "name": "Bankaufsichtliche Anforderungen an die IT (BAIT)",
        "name_en": "Supervisory Requirements for IT in Financial Institutions (BAIT)",
        "name_zh": "銀行業 IT 監管要求",
        "regulation_type": "指引",
        "issuing_authority": "BaFin",
        "search_keywords": ["BaFin BAIT", "BAIT Bankaufsichtliche"],
    },
    {
        "name": "Versicherungsaufsichtliche Anforderungen an die IT (VAIT)",
        "name_en": "Supervisory Requirements for IT in Insurance Companies (VAIT)",
        "name_zh": "保險業 IT 監管要求",
        "regulation_type": "指引",
        "issuing_authority": "BaFin",
        "search_keywords": ["BaFin VAIT", "VAIT Versicherungsaufsichtliche"],
    },
    {
        "name": "Mindestanforderungen an das Risikomanagement (MaRisk)",
        "name_en": "Minimum Requirements for Risk Management (MaRisk)",
        "name_zh": "風險管理最低要求",
        "regulation_type": "指引",
        "issuing_authority": "BaFin",
        "search_keywords": ["BaFin MaRisk", "MaRisk Mindestanforderungen"],
    },
]


# ============================================================
# 歐盟金融業資安法規
# ============================================================

EU_REGULATIONS = [
    {
        "name": "Digital Operational Resilience Act (DORA)",
        "name_en": "Digital Operational Resilience Act (DORA)",
        "name_zh": "數位營運韌性法案",
        "regulation_type": "規則",
        "issuing_authority": "European Union",
        "search_keywords": ["EU DORA regulation", "Digital Operational Resilience Act"],
    },
    {
        "name": "Network and Information Security Directive 2 (NIS2)",
        "name_en": "Network and Information Security Directive 2 (NIS2)",
        "name_zh": "網路與資訊安全指令 2",
        "regulation_type": "指令",
        "issuing_authority": "European Union",
        "search_keywords": ["NIS2 Directive", "NIS2 financial sector"],
    },
    {
        "name": "General Data Protection Regulation (GDPR)",
        "name_en": "General Data Protection Regulation (GDPR)",
        "name_zh": "一般資料保護規則",
        "regulation_type": "規則",
        "issuing_authority": "European Union",
        "search_keywords": ["GDPR", "EU data protection regulation"],
    },
    {
        "name": "Payment Services Directive 2 (PSD2)",
        "name_en": "Payment Services Directive 2 (PSD2)",
        "name_zh": "支付服務指令 2",
        "regulation_type": "指令",
        "issuing_authority": "European Union",
        "search_keywords": ["PSD2", "Payment Services Directive security"],
    },
]


# ============================================================
# 澳洲金融業資安法規
# ============================================================

AUSTRALIA_REGULATIONS = [
    {
        "name": "Prudential Standard CPS 234 Information Security",
        "name_en": "Prudential Standard CPS 234 Information Security",
        "name_zh": "審慎標準 CPS 234 資訊安全",
        "regulation_type": "審慎標準",
        "issuing_authority": "APRA",
        "search_keywords": ["APRA CPS 234", "CPS 234 Information Security"],
    },
    {
        "name": "Prudential Standard CPS 230 Operational Risk Management",
        "name_en": "Prudential Standard CPS 230 Operational Risk Management",
        "name_zh": "審慎標準 CPS 230 營運風險管理",
        "regulation_type": "審慎標準",
        "issuing_authority": "APRA",
        "search_keywords": ["APRA CPS 230", "CPS 230 Operational Risk"],
    },
    {
        "name": "Privacy Act 1988",
        "name_en": "Privacy Act 1988",
        "name_zh": "隱私法",
        "regulation_type": "法律",
        "issuing_authority": "Australian Government",
        "search_keywords": ["Australia Privacy Act", "Privacy Act 1988"],
    },
]


# ============================================================
# 美國金融業資安法規
# ============================================================

US_REGULATIONS = [
    {
        "name": "Gramm-Leach-Bliley Act (GLBA)",
        "name_en": "Gramm-Leach-Bliley Act (GLBA)",
        "name_zh": "金融服務現代化法案",
        "regulation_type": "法律",
        "issuing_authority": "US Congress",
        "search_keywords": ["GLBA", "Gramm-Leach-Bliley Act"],
    },
    {
        "name": "NIST Cybersecurity Framework",
        "name_en": "NIST Cybersecurity Framework",
        "name_zh": "NIST 網路安全框架",
        "regulation_type": "框架",
        "issuing_authority": "NIST",
        "search_keywords": ["NIST Cybersecurity Framework", "NIST CSF"],
    },
    {
        "name": "FFIEC IT Examination Handbook",
        "name_en": "FFIEC IT Examination Handbook",
        "name_zh": "FFIEC IT 檢查手冊",
        "regulation_type": "指引",
        "issuing_authority": "FFIEC",
        "search_keywords": ["FFIEC IT Examination Handbook", "FFIEC cybersecurity"],
    },
    {
        "name": "New York DFS Cybersecurity Regulation (23 NYCRR 500)",
        "name_en": "New York DFS Cybersecurity Regulation",
        "name_zh": "紐約金融服務局網路安全法規",
        "regulation_type": "規則",
        "issuing_authority": "NY DFS",
        "search_keywords": ["23 NYCRR 500", "NY DFS Cybersecurity"],
    },
]


# ============================================================
# 匯入函數
# ============================================================

def seed_regulations():
    """匯入所有必搜法規"""
    print("=" * 60)
    print("[Seed] 開始匯入必搜法規...")
    print("=" * 60)

    manager = BaselineManager()

    # 定義各國法規資料
    ALL_REGULATIONS = [
        ("JP", "finance_general", "cybersecurity", JAPAN_REGULATIONS),
        ("SG", "finance_general", "cybersecurity", SINGAPORE_REGULATIONS),
        ("KR", "finance_general", "cybersecurity", KOREA_REGULATIONS),
        ("TW", "finance_general", "cybersecurity", TAIWAN_REGULATIONS),
        ("DE", "finance_general", "cybersecurity", GERMANY_REGULATIONS),
        ("EU", "finance_general", "cybersecurity", EU_REGULATIONS),
        ("AU", "finance_general", "cybersecurity", AUSTRALIA_REGULATIONS),
        ("US", "finance_general", "cybersecurity", US_REGULATIONS),
    ]

    total_count = 0

    for country_code, industry_code, topic_code, regulations in ALL_REGULATIONS:
        print(f"\n[{country_code}] 匯入 {len(regulations)} 筆法規...")

        for reg in regulations:
            manager.add_regulation(
                name=reg["name"],
                name_en=reg.get("name_en"),
                name_zh=reg.get("name_zh"),
                country_code=country_code,
                industry_code=industry_code,
                topic_code=topic_code,
                regulation_type=reg.get("regulation_type"),
                issuing_authority=reg.get("issuing_authority"),
                official_url=reg.get("official_url"),
                search_keywords=reg.get("search_keywords"),
                is_mandatory=True,
                source="manual",
            )
            total_count += 1

    print("\n" + "=" * 60)
    print(f"[Seed] 匯入完成! 共 {total_count} 筆必搜法規")
    print("=" * 60)

    # 顯示統計
    stats = manager.get_statistics()
    print("\n統計:")
    print(f"  - 法規總數: {stats['total']} 筆")
    print(f"  - 必搜法規: {stats['mandatory']} 筆")
    print("\n按國家:")
    for country, count in stats["by_country"].items():
        print(f"    {country}: {count} 筆")

    manager.close()


if __name__ == "__main__":
    seed_regulations()
