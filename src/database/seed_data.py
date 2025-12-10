"""
資料庫種子資料

包含:
- 40 個 Custom Search API 支援的國家/地區
- 30 大產業別
- 常見法規主題
"""

from datetime import datetime
from .models import (
    Country,
    Industry,
    Topic,
    RegulationBaseline,
    get_session,
    init_database,
)


# ============================================================
# 國家/地區資料 (40 個)
# ============================================================

COUNTRIES = [
    # ===== 東亞 (6) =====
    {"code": "TW", "name_zh": "台灣", "name_en": "Taiwan", "region": "東亞"},
    {"code": "JP", "name_zh": "日本", "name_en": "Japan", "region": "東亞"},
    {"code": "KR", "name_zh": "韓國", "name_en": "South Korea", "region": "東亞"},
    {"code": "CN", "name_zh": "中國", "name_en": "China", "region": "東亞"},
    {"code": "HK", "name_zh": "香港", "name_en": "Hong Kong", "region": "東亞"},
    {"code": "MO", "name_zh": "澳門", "name_en": "Macau", "region": "東亞"},

    # ===== 東南亞 (6) =====
    {"code": "SG", "name_zh": "新加坡", "name_en": "Singapore", "region": "東南亞"},
    {"code": "MY", "name_zh": "馬來西亞", "name_en": "Malaysia", "region": "東南亞"},
    {"code": "TH", "name_zh": "泰國", "name_en": "Thailand", "region": "東南亞"},
    {"code": "ID", "name_zh": "印尼", "name_en": "Indonesia", "region": "東南亞"},
    {"code": "VN", "name_zh": "越南", "name_en": "Vietnam", "region": "東南亞"},
    {"code": "PH", "name_zh": "菲律賓", "name_en": "Philippines", "region": "東南亞"},

    # ===== 南亞 (3) =====
    {"code": "IN", "name_zh": "印度", "name_en": "India", "region": "南亞"},
    {"code": "PK", "name_zh": "巴基斯坦", "name_en": "Pakistan", "region": "南亞"},
    {"code": "BD", "name_zh": "孟加拉", "name_en": "Bangladesh", "region": "南亞"},

    # ===== 中東 (4) =====
    {"code": "AE", "name_zh": "阿聯酋", "name_en": "United Arab Emirates", "region": "中東"},
    {"code": "SA", "name_zh": "沙烏地阿拉伯", "name_en": "Saudi Arabia", "region": "中東"},
    {"code": "IL", "name_zh": "以色列", "name_en": "Israel", "region": "中東"},
    {"code": "TR", "name_zh": "土耳其", "name_en": "Turkey", "region": "中東"},

    # ===== 歐洲 (12) =====
    {"code": "EU", "name_zh": "歐盟", "name_en": "European Union", "region": "歐洲"},
    {"code": "GB", "name_zh": "英國", "name_en": "United Kingdom", "region": "歐洲"},
    {"code": "DE", "name_zh": "德國", "name_en": "Germany", "region": "歐洲"},
    {"code": "FR", "name_zh": "法國", "name_en": "France", "region": "歐洲"},
    {"code": "IT", "name_zh": "義大利", "name_en": "Italy", "region": "歐洲"},
    {"code": "ES", "name_zh": "西班牙", "name_en": "Spain", "region": "歐洲"},
    {"code": "NL", "name_zh": "荷蘭", "name_en": "Netherlands", "region": "歐洲"},
    {"code": "CH", "name_zh": "瑞士", "name_en": "Switzerland", "region": "歐洲"},
    {"code": "SE", "name_zh": "瑞典", "name_en": "Sweden", "region": "歐洲"},
    {"code": "PL", "name_zh": "波蘭", "name_en": "Poland", "region": "歐洲"},
    {"code": "RU", "name_zh": "俄羅斯", "name_en": "Russia", "region": "歐洲"},

    # ===== 北美 (3) =====
    {"code": "US", "name_zh": "美國", "name_en": "United States", "region": "北美"},
    {"code": "CA", "name_zh": "加拿大", "name_en": "Canada", "region": "北美"},
    {"code": "MX", "name_zh": "墨西哥", "name_en": "Mexico", "region": "北美"},

    # ===== 南美 (4) =====
    {"code": "BR", "name_zh": "巴西", "name_en": "Brazil", "region": "南美"},
    {"code": "AR", "name_zh": "阿根廷", "name_en": "Argentina", "region": "南美"},
    {"code": "CL", "name_zh": "智利", "name_en": "Chile", "region": "南美"},
    {"code": "CO", "name_zh": "哥倫比亞", "name_en": "Colombia", "region": "南美"},

    # ===== 大洋洲 (2) =====
    {"code": "AU", "name_zh": "澳洲", "name_en": "Australia", "region": "大洋洲"},
    {"code": "NZ", "name_zh": "紐西蘭", "name_en": "New Zealand", "region": "大洋洲"},

    # ===== 非洲 (4) =====
    {"code": "ZA", "name_zh": "南非", "name_en": "South Africa", "region": "非洲"},
    {"code": "NG", "name_zh": "奈及利亞", "name_en": "Nigeria", "region": "非洲"},
    {"code": "KE", "name_zh": "肯亞", "name_en": "Kenya", "region": "非洲"},
    {"code": "EG", "name_zh": "埃及", "name_en": "Egypt", "region": "非洲"},
]


# ============================================================
# 產業別資料 (30 大產業)
# ============================================================

INDUSTRIES = [
    # ===== 金融服務業 (5) =====
    {
        "code": "banking",
        "name_zh": "銀行業",
        "name_en": "Banking",
        "category": "金融服務",
        "description": "商業銀行、投資銀行、信用合作社等",
        "keywords": ["bank", "banking", "銀行", "信用", "存款", "貸款"],
    },
    {
        "code": "securities",
        "name_zh": "證券業",
        "name_en": "Securities",
        "category": "金融服務",
        "description": "證券商、投資顧問、資產管理等",
        "keywords": ["securities", "investment", "證券", "投資", "股票", "基金"],
    },
    {
        "code": "insurance",
        "name_zh": "保險業",
        "name_en": "Insurance",
        "category": "金融服務",
        "description": "壽險、產險、再保險等",
        "keywords": ["insurance", "保險", "壽險", "產險"],
    },
    {
        "code": "fintech",
        "name_zh": "金融科技",
        "name_en": "FinTech",
        "category": "金融服務",
        "description": "電子支付、加密貨幣、P2P借貸等",
        "keywords": ["fintech", "payment", "crypto", "支付", "加密貨幣", "數位金融"],
    },
    {
        "code": "finance_general",
        "name_zh": "金融業（通用）",
        "name_en": "Financial Services (General)",
        "category": "金融服務",
        "description": "金融業通用法規，適用於所有金融機構",
        "keywords": ["financial", "金融", "金融機構"],
    },

    # ===== 醫療健康 (3) =====
    {
        "code": "healthcare",
        "name_zh": "醫療機構",
        "name_en": "Healthcare",
        "category": "醫療健康",
        "description": "醫院、診所、醫療中心等",
        "keywords": ["healthcare", "hospital", "醫療", "醫院", "診所"],
    },
    {
        "code": "pharmaceutical",
        "name_zh": "製藥業",
        "name_en": "Pharmaceutical",
        "category": "醫療健康",
        "description": "藥品製造、生技公司等",
        "keywords": ["pharmaceutical", "drug", "製藥", "藥品", "生技"],
    },
    {
        "code": "medical_device",
        "name_zh": "醫療器材",
        "name_en": "Medical Devices",
        "category": "醫療健康",
        "description": "醫療設備製造與銷售",
        "keywords": ["medical device", "醫療器材", "醫材"],
    },

    # ===== 科技資訊 (4) =====
    {
        "code": "technology",
        "name_zh": "科技業（通用）",
        "name_en": "Technology",
        "category": "科技資訊",
        "description": "軟體、硬體、雲端服務等",
        "keywords": ["technology", "software", "科技", "軟體", "IT"],
    },
    {
        "code": "telecom",
        "name_zh": "電信業",
        "name_en": "Telecommunications",
        "category": "科技資訊",
        "description": "電信營運商、網路服務商等",
        "keywords": ["telecom", "telecommunications", "電信", "通訊"],
    },
    {
        "code": "cloud_services",
        "name_zh": "雲端服務",
        "name_en": "Cloud Services",
        "category": "科技資訊",
        "description": "雲端運算、SaaS、IaaS等",
        "keywords": ["cloud", "SaaS", "雲端", "雲服務"],
    },
    {
        "code": "ecommerce",
        "name_zh": "電子商務",
        "name_en": "E-commerce",
        "category": "科技資訊",
        "description": "線上零售、電商平台等",
        "keywords": ["ecommerce", "e-commerce", "電商", "網購"],
    },

    # ===== 製造業 (4) =====
    {
        "code": "manufacturing",
        "name_zh": "製造業（通用）",
        "name_en": "Manufacturing",
        "category": "製造業",
        "description": "一般製造業",
        "keywords": ["manufacturing", "製造", "工廠"],
    },
    {
        "code": "automotive",
        "name_zh": "汽車業",
        "name_en": "Automotive",
        "category": "製造業",
        "description": "汽車製造、零組件等",
        "keywords": ["automotive", "vehicle", "汽車", "車輛"],
    },
    {
        "code": "semiconductor",
        "name_zh": "半導體",
        "name_en": "Semiconductor",
        "category": "製造業",
        "description": "晶片設計、晶圓製造等",
        "keywords": ["semiconductor", "chip", "半導體", "晶片"],
    },
    {
        "code": "aerospace",
        "name_zh": "航太業",
        "name_en": "Aerospace & Defense",
        "category": "製造業",
        "description": "航空、太空、國防工業",
        "keywords": ["aerospace", "defense", "航太", "國防"],
    },

    # ===== 能源公用 (3) =====
    {
        "code": "energy",
        "name_zh": "能源業",
        "name_en": "Energy",
        "category": "能源公用",
        "description": "石油、天然氣、再生能源等",
        "keywords": ["energy", "oil", "能源", "石油", "電力"],
    },
    {
        "code": "utilities",
        "name_zh": "公用事業",
        "name_en": "Utilities",
        "category": "能源公用",
        "description": "電力、水利、天然氣供應等",
        "keywords": ["utilities", "electricity", "公用事業", "水電"],
    },
    {
        "code": "critical_infrastructure",
        "name_zh": "關鍵基礎設施",
        "name_en": "Critical Infrastructure",
        "category": "能源公用",
        "description": "關鍵基礎設施營運者",
        "keywords": ["critical infrastructure", "關鍵基礎設施", "CII"],
    },

    # ===== 零售消費 (2) =====
    {
        "code": "retail",
        "name_zh": "零售業",
        "name_en": "Retail",
        "category": "零售消費",
        "description": "實體零售、連鎖商店等",
        "keywords": ["retail", "store", "零售", "商店"],
    },
    {
        "code": "consumer_goods",
        "name_zh": "消費品",
        "name_en": "Consumer Goods",
        "category": "零售消費",
        "description": "消費性產品製造",
        "keywords": ["consumer", "goods", "消費品", "快消品"],
    },

    # ===== 運輸物流 (2) =====
    {
        "code": "transportation",
        "name_zh": "運輸業",
        "name_en": "Transportation",
        "category": "運輸物流",
        "description": "航空、鐵路、海運、公路運輸",
        "keywords": ["transportation", "transport", "運輸", "交通"],
    },
    {
        "code": "logistics",
        "name_zh": "物流業",
        "name_en": "Logistics",
        "category": "運輸物流",
        "description": "倉儲、配送、供應鏈管理",
        "keywords": ["logistics", "supply chain", "物流", "倉儲"],
    },

    # ===== 其他服務業 (5) =====
    {
        "code": "education",
        "name_zh": "教育業",
        "name_en": "Education",
        "category": "其他服務",
        "description": "學校、補習班、線上教育等",
        "keywords": ["education", "school", "教育", "學校"],
    },
    {
        "code": "real_estate",
        "name_zh": "不動產",
        "name_en": "Real Estate",
        "category": "其他服務",
        "description": "不動產開發、仲介、物業管理",
        "keywords": ["real estate", "property", "不動產", "房地產"],
    },
    {
        "code": "hospitality",
        "name_zh": "餐旅業",
        "name_en": "Hospitality",
        "category": "其他服務",
        "description": "飯店、餐飲、旅遊業",
        "keywords": ["hospitality", "hotel", "餐旅", "飯店"],
    },
    {
        "code": "media",
        "name_zh": "媒體娛樂",
        "name_en": "Media & Entertainment",
        "category": "其他服務",
        "description": "影視、遊戲、廣告等",
        "keywords": ["media", "entertainment", "媒體", "娛樂"],
    },
    {
        "code": "professional_services",
        "name_zh": "專業服務",
        "name_en": "Professional Services",
        "category": "其他服務",
        "description": "法律、會計、顧問等",
        "keywords": ["professional", "consulting", "專業服務", "顧問"],
    },

    # ===== 政府與公共 (2) =====
    {
        "code": "government",
        "name_zh": "政府機關",
        "name_en": "Government",
        "category": "政府公共",
        "description": "中央與地方政府機關",
        "keywords": ["government", "public sector", "政府", "公部門"],
    },
    {
        "code": "public_services",
        "name_zh": "公共服務",
        "name_en": "Public Services",
        "category": "政府公共",
        "description": "公共服務機構",
        "keywords": ["public service", "公共服務"],
    },
]


# ============================================================
# 法規主題資料
# ============================================================

TOPICS = [
    {
        "code": "cybersecurity",
        "name_zh": "資訊安全",
        "name_en": "Cybersecurity",
        "description": "網路安全、資訊安全管理、資安事件通報等",
        "keywords": {
            "zh": ["資安", "資訊安全", "網路安全", "cyber"],
            "en": ["cybersecurity", "information security", "cyber risk"],
            "ja": ["サイバーセキュリティ", "情報セキュリティ", "サイバー攻撃"],
            "ko": ["사이버보안", "정보보안", "사이버 공격"],
        },
    },
    {
        "code": "privacy",
        "name_zh": "個人資料保護",
        "name_en": "Data Privacy",
        "description": "個資保護、隱私權、資料處理等",
        "keywords": {
            "zh": ["個資", "個人資料", "隱私", "資料保護"],
            "en": ["privacy", "personal data", "data protection", "GDPR"],
            "ja": ["個人情報", "プライバシー", "データ保護"],
            "ko": ["개인정보", "프라이버시", "데이터 보호"],
        },
    },
    {
        "code": "aml",
        "name_zh": "反洗錢",
        "name_en": "Anti-Money Laundering",
        "description": "反洗錢、反恐融資、KYC等",
        "keywords": {
            "zh": ["反洗錢", "洗錢防制", "KYC", "客戶審查"],
            "en": ["AML", "anti-money laundering", "KYC", "CFT"],
            "ja": ["マネーロンダリング", "資金洗浄", "本人確認"],
            "ko": ["자금세탁방지", "고객확인제도"],
        },
    },
    {
        "code": "it_governance",
        "name_zh": "IT 治理",
        "name_en": "IT Governance",
        "description": "IT 風險管理、系統管理、委外管理等",
        "keywords": {
            "zh": ["IT治理", "資訊治理", "系統風險", "委外"],
            "en": ["IT governance", "IT risk", "outsourcing", "vendor management"],
            "ja": ["ITガバナンス", "システムリスク", "外部委託"],
            "ko": ["IT 거버넌스", "시스템 리스크", "외부위탁"],
        },
    },
    {
        "code": "cloud",
        "name_zh": "雲端安全",
        "name_en": "Cloud Security",
        "description": "雲端服務、雲端安全、資料本地化等",
        "keywords": {
            "zh": ["雲端", "雲端安全", "資料在地化"],
            "en": ["cloud", "cloud security", "data localization"],
            "ja": ["クラウド", "クラウドセキュリティ"],
            "ko": ["클라우드", "클라우드 보안"],
        },
    },
    {
        "code": "operational_resilience",
        "name_zh": "營運韌性",
        "name_en": "Operational Resilience",
        "description": "業務連續性、災難復原、營運韌性等",
        "keywords": {
            "zh": ["營運韌性", "業務連續", "災難復原", "BCP"],
            "en": ["operational resilience", "business continuity", "disaster recovery"],
            "ja": ["オペレーショナルレジリエンス", "事業継続", "災害復旧"],
            "ko": ["운영 복원력", "업무 연속성", "재해 복구"],
        },
    },
    {
        "code": "ai_regulation",
        "name_zh": "AI 治理",
        "name_en": "AI Regulation",
        "description": "人工智慧監管、演算法治理、AI倫理等",
        "keywords": {
            "zh": ["AI", "人工智慧", "演算法", "機器學習"],
            "en": ["AI", "artificial intelligence", "algorithm", "machine learning"],
            "ja": ["AI", "人工知能", "アルゴリズム"],
            "ko": ["AI", "인공지능", "알고리즘"],
        },
    },
    {
        "code": "digital_assets",
        "name_zh": "數位資產",
        "name_en": "Digital Assets",
        "description": "加密貨幣、虛擬資產、NFT等",
        "keywords": {
            "zh": ["加密貨幣", "虛擬資產", "數位資產", "NFT"],
            "en": ["crypto", "digital assets", "virtual assets", "cryptocurrency"],
            "ja": ["暗号資産", "仮想通貨", "デジタル資産"],
            "ko": ["암호화폐", "가상자산", "디지털 자산"],
        },
    },
]


# ============================================================
# 初始化函數
# ============================================================

def seed_countries(session):
    """匯入國家資料"""
    print("[Seed] 匯入國家資料...")
    count = 0
    for data in COUNTRIES:
        existing = session.query(Country).filter_by(code=data["code"]).first()
        if not existing:
            country = Country(**data)
            session.add(country)
            count += 1
    session.commit()
    print(f"[Seed] 已新增 {count} 個國家，共 {len(COUNTRIES)} 個")


def seed_industries(session):
    """匯入產業資料"""
    print("[Seed] 匯入產業資料...")
    count = 0
    for data in INDUSTRIES:
        existing = session.query(Industry).filter_by(code=data["code"]).first()
        if not existing:
            industry = Industry(**data)
            session.add(industry)
            count += 1
    session.commit()
    print(f"[Seed] 已新增 {count} 個產業，共 {len(INDUSTRIES)} 個")


def seed_topics(session):
    """匯入主題資料"""
    print("[Seed] 匯入主題資料...")
    count = 0
    for data in TOPICS:
        existing = session.query(Topic).filter_by(code=data["code"]).first()
        if not existing:
            topic = Topic(**data)
            session.add(topic)
            count += 1
    session.commit()
    print(f"[Seed] 已新增 {count} 個主題，共 {len(TOPICS)} 個")


def seed_all():
    """執行所有種子資料匯入"""
    print("=" * 60)
    print("[Seed] 開始匯入種子資料...")
    print("=" * 60)

    # 初始化資料庫
    init_database()

    # 取得 session
    session = get_session()

    try:
        seed_countries(session)
        seed_industries(session)
        seed_topics(session)

        print("=" * 60)
        print("[Seed] 種子資料匯入完成!")
        print("=" * 60)

        # 顯示統計
        print(f"\n統計:")
        print(f"  - 國家/地區: {session.query(Country).count()} 個")
        print(f"  - 產業別: {session.query(Industry).count()} 個")
        print(f"  - 法規主題: {session.query(Topic).count()} 個")
        print(f"  - 法規 Baseline: {session.query(RegulationBaseline).count()} 筆")

    except Exception as e:
        session.rollback()
        print(f"[Seed] 錯誤: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_all()
