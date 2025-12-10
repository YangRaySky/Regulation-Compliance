"""
其他產業法規種子資料

新增醫療、科技、電信、電商、製造等產業的法規
"""

from .models import get_session, RegulationBaseline, init_database
from datetime import datetime


# === 醫療產業法規 ===
HEALTHCARE_REGULATIONS = [
    # 美國
    {
        "country_code": "US",
        "name": "Health Insurance Portability and Accountability Act (HIPAA)",
        "name_en": "Health Insurance Portability and Accountability Act",
        "name_zh": "健康保險可攜性與責任法案",
        "industry_code": "healthcare",
        "topic_code": "privacy",
        "regulation_type": "法律",
        "issuing_authority": "U.S. Department of Health and Human Services",
        "search_keywords": ["HIPAA", "HIPAA Privacy Rule", "HIPAA Security Rule"],
        "applicable_industries": ["healthcare", "pharmaceutical", "medical_device", "insurance"],
        "is_cross_industry": False,
    },
    {
        "country_code": "US",
        "name": "HITECH Act",
        "name_en": "Health Information Technology for Economic and Clinical Health Act",
        "name_zh": "健康資訊科技經濟與臨床健康法案",
        "industry_code": "healthcare",
        "topic_code": "cybersecurity",
        "regulation_type": "法律",
        "issuing_authority": "U.S. Department of Health and Human Services",
        "search_keywords": ["HITECH Act", "Health IT"],
        "applicable_industries": ["healthcare", "technology"],
        "is_cross_industry": False,
    },
    {
        "country_code": "US",
        "name": "FDA 21 CFR Part 11",
        "name_en": "FDA Electronic Records and Electronic Signatures",
        "name_zh": "FDA 電子記錄與電子簽章規定",
        "industry_code": "pharmaceutical",
        "topic_code": "it_governance",
        "regulation_type": "規則",
        "issuing_authority": "U.S. Food and Drug Administration",
        "search_keywords": ["FDA 21 CFR Part 11", "FDA electronic records"],
        "applicable_industries": ["pharmaceutical", "medical_device", "healthcare"],
        "is_cross_industry": False,
    },
    # 歐盟
    {
        "country_code": "EU",
        "name": "Medical Device Regulation (MDR)",
        "name_en": "Medical Device Regulation",
        "name_zh": "醫療器材法規",
        "industry_code": "medical_device",
        "topic_code": "it_governance",
        "regulation_type": "Regulation",
        "issuing_authority": "European Commission",
        "search_keywords": ["EU MDR", "Medical Device Regulation 2017/745"],
        "applicable_industries": ["medical_device", "healthcare"],
        "is_cross_industry": False,
    },
    {
        "country_code": "EU",
        "name": "In Vitro Diagnostic Regulation (IVDR)",
        "name_en": "In Vitro Diagnostic Medical Devices Regulation",
        "name_zh": "體外診斷醫療器材法規",
        "industry_code": "medical_device",
        "topic_code": "it_governance",
        "regulation_type": "Regulation",
        "issuing_authority": "European Commission",
        "search_keywords": ["EU IVDR", "In Vitro Diagnostic Regulation"],
        "applicable_industries": ["medical_device", "healthcare"],
        "is_cross_industry": False,
    },
    # 台灣
    {
        "country_code": "TW",
        "name": "醫療機構電子病歷製作及管理辦法",
        "name_en": "Regulations for Electronic Medical Records",
        "name_zh": "醫療機構電子病歷製作及管理辦法",
        "industry_code": "healthcare",
        "topic_code": "it_governance",
        "regulation_type": "辦法",
        "issuing_authority": "衛生福利部",
        "search_keywords": ["電子病歷", "醫療機構電子病歷"],
        "applicable_industries": ["healthcare"],
        "is_cross_industry": False,
    },
    # 日本
    {
        "country_code": "JP",
        "name": "医療情報システムの安全管理に関するガイドライン",
        "name_en": "Guidelines for Security Management of Medical Information Systems",
        "name_zh": "醫療資訊系統安全管理指引",
        "industry_code": "healthcare",
        "topic_code": "cybersecurity",
        "regulation_type": "指引",
        "issuing_authority": "厚生労働省",
        "search_keywords": ["医療情報システム 安全管理 ガイドライン", "厚労省 医療情報"],
        "applicable_industries": ["healthcare"],
        "is_cross_industry": False,
    },
]

# === 電信產業法規 ===
TELECOM_REGULATIONS = [
    # 美國
    {
        "country_code": "US",
        "name": "Communications Act of 1934 (as amended)",
        "name_en": "Communications Act",
        "name_zh": "通訊法",
        "industry_code": "telecom",
        "topic_code": "it_governance",
        "regulation_type": "法律",
        "issuing_authority": "Federal Communications Commission",
        "search_keywords": ["Communications Act FCC", "FCC regulations"],
        "applicable_industries": ["telecom"],
        "is_cross_industry": False,
    },
    {
        "country_code": "US",
        "name": "FCC Customer Proprietary Network Information (CPNI) Rules",
        "name_en": "CPNI Rules",
        "name_zh": "客戶專屬網路資訊規則",
        "industry_code": "telecom",
        "topic_code": "privacy",
        "regulation_type": "規則",
        "issuing_authority": "Federal Communications Commission",
        "search_keywords": ["FCC CPNI", "Customer Proprietary Network Information"],
        "applicable_industries": ["telecom"],
        "is_cross_industry": False,
    },
    # 歐盟
    {
        "country_code": "EU",
        "name": "European Electronic Communications Code (EECC)",
        "name_en": "European Electronic Communications Code",
        "name_zh": "歐洲電子通訊法典",
        "industry_code": "telecom",
        "topic_code": "it_governance",
        "regulation_type": "Directive",
        "issuing_authority": "European Commission",
        "search_keywords": ["EECC", "European Electronic Communications Code"],
        "applicable_industries": ["telecom"],
        "is_cross_industry": False,
    },
    {
        "country_code": "EU",
        "name": "ePrivacy Directive",
        "name_en": "Directive on Privacy and Electronic Communications",
        "name_zh": "電子隱私指令",
        "industry_code": "telecom",
        "topic_code": "privacy",
        "regulation_type": "Directive",
        "issuing_authority": "European Commission",
        "search_keywords": ["ePrivacy Directive", "cookie directive"],
        "applicable_industries": ["telecom", "technology", "ecommerce"],
        "is_cross_industry": False,
    },
    # 台灣
    {
        "country_code": "TW",
        "name": "電信管理法",
        "name_en": "Telecommunications Management Act",
        "name_zh": "電信管理法",
        "industry_code": "telecom",
        "topic_code": "it_governance",
        "regulation_type": "法律",
        "issuing_authority": "國家通訊傳播委員會",
        "search_keywords": ["電信管理法", "NCC 電信"],
        "applicable_industries": ["telecom"],
        "is_cross_industry": False,
    },
]

# === 電商/科技產業法規 ===
TECH_ECOMMERCE_REGULATIONS = [
    # 歐盟
    {
        "country_code": "EU",
        "name": "Digital Services Act (DSA)",
        "name_en": "Digital Services Act",
        "name_zh": "數位服務法",
        "industry_code": "technology",
        "topic_code": "it_governance",
        "regulation_type": "Regulation",
        "issuing_authority": "European Commission",
        "search_keywords": ["EU DSA", "Digital Services Act"],
        "applicable_industries": ["technology", "ecommerce", "social_media"],
        "is_cross_industry": False,
    },
    {
        "country_code": "EU",
        "name": "Digital Markets Act (DMA)",
        "name_en": "Digital Markets Act",
        "name_zh": "數位市場法",
        "industry_code": "technology",
        "topic_code": "it_governance",
        "regulation_type": "Regulation",
        "issuing_authority": "European Commission",
        "search_keywords": ["EU DMA", "Digital Markets Act"],
        "applicable_industries": ["technology", "ecommerce"],
        "is_cross_industry": False,
    },
    {
        "country_code": "EU",
        "name": "AI Act",
        "name_en": "Artificial Intelligence Act",
        "name_zh": "人工智慧法",
        "industry_code": "technology",
        "topic_code": "ai_regulation",
        "regulation_type": "Regulation",
        "issuing_authority": "European Commission",
        "search_keywords": ["EU AI Act", "Artificial Intelligence Act"],
        "applicable_industries": ["technology", "healthcare", "finance_general", "manufacturing"],
        "is_cross_industry": True,
    },
    # 中國
    {
        "country_code": "CN",
        "name": "电子商务法",
        "name_en": "E-Commerce Law",
        "name_zh": "電子商務法",
        "industry_code": "ecommerce",
        "topic_code": "it_governance",
        "regulation_type": "法律",
        "issuing_authority": "全国人民代表大会常务委员会",
        "search_keywords": ["中国电子商务法", "E-Commerce Law China"],
        "applicable_industries": ["ecommerce", "technology", "retail"],
        "is_cross_industry": False,
    },
    {
        "country_code": "CN",
        "name": "生成式人工智能服务管理暂行办法",
        "name_en": "Interim Measures for the Management of Generative AI Services",
        "name_zh": "生成式人工智能服務管理暫行辦法",
        "industry_code": "technology",
        "topic_code": "ai_regulation",
        "regulation_type": "辦法",
        "issuing_authority": "国家互联网信息办公室",
        "search_keywords": ["生成式人工智能 管理办法", "China generative AI"],
        "applicable_industries": ["technology"],
        "is_cross_industry": False,
    },
    # 日本
    {
        "country_code": "JP",
        "name": "特定デジタルプラットフォームの透明性及び公正性の向上に関する法律",
        "name_en": "Act on Improving Transparency and Fairness of Digital Platforms",
        "name_zh": "特定數位平台透明性及公正性提升法",
        "industry_code": "technology",
        "topic_code": "it_governance",
        "regulation_type": "法律",
        "issuing_authority": "経済産業省",
        "search_keywords": ["デジタルプラットフォーム 透明性", "Japan digital platform law"],
        "applicable_industries": ["technology", "ecommerce"],
        "is_cross_industry": False,
    },
]

# === 能源/關鍵基礎設施法規 ===
ENERGY_CRITICAL_INFRA_REGULATIONS = [
    # 美國
    {
        "country_code": "US",
        "name": "NERC Critical Infrastructure Protection (CIP) Standards",
        "name_en": "NERC CIP Standards",
        "name_zh": "NERC 關鍵基礎設施保護標準",
        "industry_code": "energy",
        "topic_code": "cybersecurity",
        "regulation_type": "標準",
        "issuing_authority": "North American Electric Reliability Corporation",
        "search_keywords": ["NERC CIP", "NERC Critical Infrastructure Protection"],
        "applicable_industries": ["energy", "utilities"],
        "is_cross_industry": False,
    },
    # 歐盟
    {
        "country_code": "EU",
        "name": "Critical Entities Resilience Directive (CER)",
        "name_en": "Critical Entities Resilience Directive",
        "name_zh": "關鍵實體韌性指令",
        "industry_code": "energy",
        "topic_code": "operational_resilience",
        "regulation_type": "Directive",
        "issuing_authority": "European Commission",
        "search_keywords": ["EU CER Directive", "Critical Entities Resilience"],
        "applicable_industries": ["energy", "utilities", "telecom", "healthcare", "finance_general"],
        "is_cross_industry": True,
    },
    # 台灣
    {
        "country_code": "TW",
        "name": "關鍵基礎設施安全防護指導綱要",
        "name_en": "Critical Infrastructure Security Protection Guidelines",
        "name_zh": "關鍵基礎設施安全防護指導綱要",
        "industry_code": "energy",
        "topic_code": "cybersecurity",
        "regulation_type": "綱要",
        "issuing_authority": "行政院",
        "search_keywords": ["關鍵基礎設施 安全防護", "CI安全防護"],
        "applicable_industries": ["energy", "utilities", "telecom", "finance_general", "healthcare"],
        "is_cross_industry": True,
    },
]

# === 製造業法規 ===
MANUFACTURING_REGULATIONS = [
    # 歐盟
    {
        "country_code": "EU",
        "name": "Cyber Resilience Act (CRA)",
        "name_en": "Cyber Resilience Act",
        "name_zh": "網路韌性法",
        "industry_code": "manufacturing",
        "topic_code": "cybersecurity",
        "regulation_type": "Regulation",
        "issuing_authority": "European Commission",
        "search_keywords": ["EU CRA", "Cyber Resilience Act"],
        "applicable_industries": ["manufacturing", "technology", "retail"],
        "is_cross_industry": False,
    },
    {
        "country_code": "EU",
        "name": "Machinery Regulation",
        "name_en": "Machinery Regulation",
        "name_zh": "機械法規",
        "industry_code": "manufacturing",
        "topic_code": "it_governance",
        "regulation_type": "Regulation",
        "issuing_authority": "European Commission",
        "search_keywords": ["EU Machinery Regulation 2023/1230"],
        "applicable_industries": ["manufacturing"],
        "is_cross_industry": False,
    },
    # 德國
    {
        "country_code": "DE",
        "name": "IT-Sicherheitsgesetz 2.0",
        "name_en": "IT Security Act 2.0",
        "name_zh": "資訊安全法 2.0",
        "industry_code": "manufacturing",
        "topic_code": "cybersecurity",
        "regulation_type": "法律",
        "issuing_authority": "Bundesministerium des Innern",
        "search_keywords": ["IT-Sicherheitsgesetz 2.0", "Germany IT Security Act"],
        "applicable_industries": ["manufacturing", "energy", "telecom", "healthcare"],
        "is_cross_industry": True,
    },
]


def seed_other_industries():
    """匯入其他產業的法規"""
    init_database()
    session = get_session()

    all_regulations = (
        HEALTHCARE_REGULATIONS +
        TELECOM_REGULATIONS +
        TECH_ECOMMERCE_REGULATIONS +
        ENERGY_CRITICAL_INFRA_REGULATIONS +
        MANUFACTURING_REGULATIONS
    )

    added = 0
    skipped = 0

    for reg_data in all_regulations:
        # 檢查是否已存在
        existing = session.query(RegulationBaseline).filter_by(
            name=reg_data["name"],
            country_code=reg_data["country_code"]
        ).first()

        if existing:
            skipped += 1
            continue

        reg = RegulationBaseline(
            name=reg_data["name"],
            name_en=reg_data.get("name_en"),
            name_zh=reg_data.get("name_zh"),
            country_code=reg_data["country_code"],
            industry_code=reg_data["industry_code"],
            topic_code=reg_data["topic_code"],
            regulation_type=reg_data.get("regulation_type"),
            issuing_authority=reg_data.get("issuing_authority"),
            search_keywords=reg_data.get("search_keywords", []),
            applicable_industries=reg_data.get("applicable_industries", []),
            is_cross_industry=reg_data.get("is_cross_industry", False),
            is_mandatory=True,
            confidence_score=0.8,
            source="seed",
        )
        session.add(reg)
        added += 1

    session.commit()
    session.close()

    print(f"=== 其他產業法規匯入完成 ===")
    print(f"新增: {added} 筆")
    print(f"跳過（已存在）: {skipped} 筆")


def print_industry_summary():
    """顯示各產業法規統計"""
    session = get_session()
    regulations = session.query(RegulationBaseline).all()

    # 統計各產業
    industry_counts = {}
    for reg in regulations:
        ind = reg.industry_code
        industry_counts[ind] = industry_counts.get(ind, 0) + 1

    print("\n=== 各產業法規統計 ===")
    for ind, count in sorted(industry_counts.items(), key=lambda x: -x[1]):
        print(f"  {ind}: {count} 筆")

    session.close()


if __name__ == "__main__":
    seed_other_industries()
    print_industry_summary()
