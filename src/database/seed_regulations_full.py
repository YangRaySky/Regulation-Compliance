"""
完整版必搜法規清單

涵蓋所有 43 個國家/地區的金融業資安相關法規
"""

from .manager import BaselineManager


# ============================================================
# 東亞地區
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
    {
        "name": "정보통신망 이용촉진 및 정보보호 등에 관한 법률",
        "name_en": "Act on Promotion of Information and Communications Network Utilization and Information Protection",
        "name_zh": "資通網路法",
        "regulation_type": "法律",
        "issuing_authority": "과학기술정보통신부",
        "search_keywords": ["정보통신망법", "Korea Network Act cybersecurity"],
    },
]

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
    {
        "name": "金融機構作業委託他人處理內部作業制度及程序辦法",
        "name_en": "Regulations Governing Internal Operating Systems and Procedures for Outsourcing of Financial Institutions",
        "name_zh": "金融機構委外辦法",
        "regulation_type": "辦法",
        "issuing_authority": "金管會",
        "search_keywords": ["金融機構 委外 辦法", "金管會 委託他人處理"],
    },
]

CHINA_REGULATIONS = [
    {
        "name": "网络安全法",
        "name_en": "Cybersecurity Law",
        "name_zh": "網路安全法",
        "regulation_type": "法律",
        "issuing_authority": "全国人民代表大会",
        "search_keywords": ["网络安全法", "China Cybersecurity Law"],
    },
    {
        "name": "数据安全法",
        "name_en": "Data Security Law",
        "name_zh": "資料安全法",
        "regulation_type": "法律",
        "issuing_authority": "全国人民代表大会",
        "search_keywords": ["数据安全法", "China Data Security Law"],
    },
    {
        "name": "个人信息保护法",
        "name_en": "Personal Information Protection Law",
        "name_zh": "個人資訊保護法",
        "regulation_type": "法律",
        "issuing_authority": "全国人民代表大会",
        "search_keywords": ["个人信息保护法", "China PIPL personal information"],
    },
    {
        "name": "金融数据安全 数据安全分级指南",
        "name_en": "Financial Data Security - Data Security Classification Guidelines",
        "name_zh": "金融數據安全分級指南",
        "regulation_type": "標準",
        "issuing_authority": "中国人民银行",
        "search_keywords": ["金融数据安全 分级", "PBOC data security classification"],
    },
    {
        "name": "银行业金融机构数据治理指引",
        "name_en": "Guidelines on Data Governance of Banking Financial Institutions",
        "name_zh": "銀行業金融機構數據治理指引",
        "regulation_type": "指引",
        "issuing_authority": "银保监会",
        "search_keywords": ["银行业 数据治理 指引", "CBIRC data governance"],
    },
]

HONGKONG_REGULATIONS = [
    {
        "name": "Supervisory Policy Manual TM-E-1 Risk Management of E-banking",
        "name_en": "Supervisory Policy Manual TM-E-1 Risk Management of E-banking",
        "name_zh": "電子銀行風險管理指引",
        "regulation_type": "指引",
        "issuing_authority": "HKMA",
        "search_keywords": ["HKMA TM-E-1 e-banking", "HKMA e-banking risk management"],
    },
    {
        "name": "Supervisory Policy Manual TM-G-1 General Principles for Technology Risk Management",
        "name_en": "Supervisory Policy Manual TM-G-1 Technology Risk Management",
        "name_zh": "科技風險管理一般原則",
        "regulation_type": "指引",
        "issuing_authority": "HKMA",
        "search_keywords": ["HKMA TM-G-1 technology risk", "HKMA technology risk management"],
    },
    {
        "name": "Cybersecurity Fortification Initiative (CFI)",
        "name_en": "Cybersecurity Fortification Initiative",
        "name_zh": "網絡安全防護計劃",
        "regulation_type": "計劃",
        "issuing_authority": "HKMA",
        "search_keywords": ["HKMA CFI cybersecurity", "Hong Kong Cybersecurity Fortification"],
    },
    {
        "name": "Personal Data (Privacy) Ordinance",
        "name_en": "Personal Data (Privacy) Ordinance",
        "name_zh": "個人資料（私隱）條例",
        "regulation_type": "條例",
        "issuing_authority": "PCPD",
        "search_keywords": ["Hong Kong PDPO", "Personal Data Privacy Ordinance Hong Kong"],
    },
]


# ============================================================
# 東南亞地區
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

MALAYSIA_REGULATIONS = [
    {
        "name": "Risk Management in Technology (RMiT)",
        "name_en": "Risk Management in Technology",
        "name_zh": "技術風險管理",
        "regulation_type": "指引",
        "issuing_authority": "BNM",
        "search_keywords": ["BNM RMiT", "Bank Negara Malaysia Risk Management Technology"],
    },
    {
        "name": "Personal Data Protection Act 2010",
        "name_en": "Personal Data Protection Act 2010",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "PDPD",
        "search_keywords": ["Malaysia PDPA 2010", "Malaysia Personal Data Protection Act"],
    },
    {
        "name": "Guidelines on Data Management and MIS Framework",
        "name_en": "Guidelines on Data Management and MIS Framework",
        "name_zh": "數據管理與管理資訊系統框架指引",
        "regulation_type": "指引",
        "issuing_authority": "BNM",
        "search_keywords": ["BNM data management guidelines", "Bank Negara data MIS"],
    },
    {
        "name": "Outsourcing Policy Document",
        "name_en": "Outsourcing Policy Document",
        "name_zh": "委外政策文件",
        "regulation_type": "政策",
        "issuing_authority": "BNM",
        "search_keywords": ["BNM outsourcing policy", "Bank Negara outsourcing"],
    },
]

THAILAND_REGULATIONS = [
    {
        "name": "พระราชบัญญัติการรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562",
        "name_en": "Cybersecurity Act B.E. 2562 (2019)",
        "name_zh": "網路安全法",
        "regulation_type": "法律",
        "issuing_authority": "NCSC",
        "search_keywords": ["Thailand Cybersecurity Act", "พระราชบัญญัติ ความมั่นคงปลอดภัยไซเบอร์"],
    },
    {
        "name": "พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562",
        "name_en": "Personal Data Protection Act B.E. 2562 (2019)",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "PDPC",
        "search_keywords": ["Thailand PDPA", "พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล"],
    },
    {
        "name": "ประกาศธนาคารแห่งประเทศไทย เรื่อง หลักเกณฑ์การกำกับดูแลความเสี่ยงด้านเทคโนโลยีสารสนเทศ",
        "name_en": "BOT Notification on IT Risk Management",
        "name_zh": "泰國央行資訊科技風險管理規定",
        "regulation_type": "規定",
        "issuing_authority": "BOT",
        "search_keywords": ["BOT IT risk management", "Bank of Thailand technology risk"],
    },
    {
        "name": "Payment Systems Act B.E. 2560",
        "name_en": "Payment Systems Act B.E. 2560 (2017)",
        "name_zh": "支付系統法",
        "regulation_type": "法律",
        "issuing_authority": "BOT",
        "search_keywords": ["Thailand Payment Systems Act", "BOT payment systems"],
    },
]

INDONESIA_REGULATIONS = [
    {
        "name": "Peraturan OJK tentang Penerapan Manajemen Risiko dalam Penggunaan Teknologi Informasi",
        "name_en": "OJK Regulation on IT Risk Management",
        "name_zh": "資訊科技風險管理規定",
        "regulation_type": "規則",
        "issuing_authority": "OJK",
        "search_keywords": ["OJK IT risk management", "OJK POJK teknologi informasi"],
    },
    {
        "name": "Undang-Undang Perlindungan Data Pribadi",
        "name_en": "Personal Data Protection Law",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "Government of Indonesia",
        "search_keywords": ["Indonesia PDP Law", "UU Perlindungan Data Pribadi"],
    },
    {
        "name": "Peraturan Bank Indonesia tentang Penyelenggaraan Teknologi Finansial",
        "name_en": "BI Regulation on Financial Technology",
        "name_zh": "金融科技監理規定",
        "regulation_type": "規則",
        "issuing_authority": "Bank Indonesia",
        "search_keywords": ["Bank Indonesia fintech regulation", "BI teknologi finansial"],
    },
]

VIETNAM_REGULATIONS = [
    {
        "name": "Luật An ninh mạng",
        "name_en": "Law on Cybersecurity",
        "name_zh": "網路安全法",
        "regulation_type": "法律",
        "issuing_authority": "National Assembly",
        "search_keywords": ["Vietnam Cybersecurity Law", "Luật An ninh mạng"],
    },
    {
        "name": "Nghị định về bảo vệ dữ liệu cá nhân",
        "name_en": "Decree on Personal Data Protection",
        "name_zh": "個人資料保護法令",
        "regulation_type": "法令",
        "issuing_authority": "Government of Vietnam",
        "search_keywords": ["Vietnam personal data protection decree", "Nghị định bảo vệ dữ liệu"],
    },
    {
        "name": "Thông tư hướng dẫn về an toàn thông tin trong hoạt động ngân hàng",
        "name_en": "Circular on Information Security in Banking",
        "name_zh": "銀行業資訊安全通報",
        "regulation_type": "通報",
        "issuing_authority": "SBV",
        "search_keywords": ["SBV information security circular", "Vietnam banking IT security"],
    },
]

PHILIPPINES_REGULATIONS = [
    {
        "name": "BSP Circular on IT Risk Management",
        "name_en": "BSP Circular on IT Risk Management",
        "name_zh": "資訊科技風險管理通報",
        "regulation_type": "通報",
        "issuing_authority": "BSP",
        "search_keywords": ["BSP IT risk management circular", "Bangko Sentral IT risk"],
    },
    {
        "name": "Data Privacy Act of 2012",
        "name_en": "Data Privacy Act of 2012",
        "name_zh": "資料隱私法",
        "regulation_type": "法律",
        "issuing_authority": "NPC",
        "search_keywords": ["Philippines Data Privacy Act", "Republic Act 10173"],
    },
    {
        "name": "Cybercrime Prevention Act of 2012",
        "name_en": "Cybercrime Prevention Act of 2012",
        "name_zh": "網路犯罪防制法",
        "regulation_type": "法律",
        "issuing_authority": "Government of Philippines",
        "search_keywords": ["Philippines Cybercrime Prevention Act", "Republic Act 10175"],
    },
]


# ============================================================
# 南亞地區
# ============================================================

INDIA_REGULATIONS = [
    {
        "name": "Information Technology Act, 2000",
        "name_en": "Information Technology Act, 2000",
        "name_zh": "資訊科技法",
        "regulation_type": "法律",
        "issuing_authority": "Government of India",
        "search_keywords": ["India IT Act 2000", "Information Technology Act India"],
    },
    {
        "name": "Digital Personal Data Protection Act, 2023",
        "name_en": "Digital Personal Data Protection Act, 2023",
        "name_zh": "數位個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "Government of India",
        "search_keywords": ["India DPDP Act 2023", "Digital Personal Data Protection Act India"],
    },
    {
        "name": "RBI Guidelines on Information Security",
        "name_en": "RBI Guidelines on Information Security",
        "name_zh": "印度央行資訊安全指引",
        "regulation_type": "指引",
        "issuing_authority": "RBI",
        "search_keywords": ["RBI information security guidelines", "Reserve Bank India cybersecurity"],
    },
    {
        "name": "RBI Master Direction on IT Governance, Risk, Controls and Assurance Practices",
        "name_en": "RBI Master Direction on IT Governance",
        "name_zh": "IT治理、風險、控制與保證實務主指令",
        "regulation_type": "指令",
        "issuing_authority": "RBI",
        "search_keywords": ["RBI IT governance master direction", "RBI ITGRC"],
    },
    {
        "name": "SEBI Cybersecurity Framework",
        "name_en": "SEBI Cybersecurity Framework",
        "name_zh": "SEBI網路安全框架",
        "regulation_type": "框架",
        "issuing_authority": "SEBI",
        "search_keywords": ["SEBI cybersecurity framework", "SEBI cyber security circular"],
    },
]


# ============================================================
# 中東地區
# ============================================================

UAE_REGULATIONS = [
    {
        "name": "Federal Decree-Law No. 45 of 2021 on Personal Data Protection",
        "name_en": "UAE Personal Data Protection Law",
        "name_zh": "阿聯酋個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "UAE Government",
        "search_keywords": ["UAE data protection law", "Federal Decree 45 2021 personal data"],
    },
    {
        "name": "CBUAE Consumer Protection Standards - Information Security",
        "name_en": "CBUAE Information Security Standards",
        "name_zh": "阿聯酋央行資訊安全標準",
        "regulation_type": "標準",
        "issuing_authority": "CBUAE",
        "search_keywords": ["CBUAE information security", "Central Bank UAE cybersecurity"],
    },
    {
        "name": "DFSA Cyber Risk Management",
        "name_en": "DFSA Cyber Risk Management",
        "name_zh": "DIFC網路風險管理",
        "regulation_type": "指引",
        "issuing_authority": "DFSA",
        "search_keywords": ["DFSA cyber risk management", "DIFC cybersecurity"],
    },
]

SAUDI_REGULATIONS = [
    {
        "name": "Personal Data Protection Law",
        "name_en": "Saudi Personal Data Protection Law",
        "name_zh": "沙烏地個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "SDAIA",
        "search_keywords": ["Saudi PDPL", "Saudi Arabia Personal Data Protection Law"],
    },
    {
        "name": "Essential Cybersecurity Controls (ECC)",
        "name_en": "Essential Cybersecurity Controls",
        "name_zh": "基本網路安全控制措施",
        "regulation_type": "標準",
        "issuing_authority": "NCA",
        "search_keywords": ["Saudi NCA ECC", "Essential Cybersecurity Controls Saudi"],
    },
    {
        "name": "SAMA Cyber Security Framework",
        "name_en": "SAMA Cyber Security Framework",
        "name_zh": "沙烏地央行網路安全框架",
        "regulation_type": "框架",
        "issuing_authority": "SAMA",
        "search_keywords": ["SAMA cybersecurity framework", "Saudi Arabia Monetary Authority cyber"],
    },
]

ISRAEL_REGULATIONS = [
    {
        "name": "Protection of Privacy Law",
        "name_en": "Protection of Privacy Law",
        "name_zh": "隱私保護法",
        "regulation_type": "法律",
        "issuing_authority": "Government of Israel",
        "search_keywords": ["Israel Privacy Protection Law", "Israel data protection"],
    },
    {
        "name": "Bank of Israel Directive on Cyber Defense Management",
        "name_en": "BOI Directive on Cyber Defense",
        "name_zh": "以色列央行網路防禦管理指令",
        "regulation_type": "指令",
        "issuing_authority": "Bank of Israel",
        "search_keywords": ["Bank of Israel cyber defense directive", "BOI cybersecurity"],
    },
]

TURKEY_REGULATIONS = [
    {
        "name": "Kişisel Verilerin Korunması Kanunu (KVKK)",
        "name_en": "Personal Data Protection Law (KVKK)",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "KVKK",
        "search_keywords": ["Turkey KVKK", "Kişisel Verilerin Korunması Kanunu"],
    },
    {
        "name": "BDDK Information Systems Regulation",
        "name_en": "BDDK Information Systems Regulation",
        "name_zh": "銀行監理機構資訊系統規定",
        "regulation_type": "規定",
        "issuing_authority": "BDDK",
        "search_keywords": ["BDDK information systems regulation", "Turkey banking IT regulation"],
    },
]


# ============================================================
# 歐洲地區
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
    {
        "name": "EBA Guidelines on ICT and Security Risk Management",
        "name_en": "EBA Guidelines on ICT and Security Risk Management",
        "name_zh": "EBA ICT與安全風險管理指引",
        "regulation_type": "指引",
        "issuing_authority": "EBA",
        "search_keywords": ["EBA ICT risk guidelines", "EBA security risk management"],
    },
]

UK_REGULATIONS = [
    {
        "name": "Financial Conduct Authority (FCA) Operational Resilience",
        "name_en": "FCA Operational Resilience Rules",
        "name_zh": "FCA營運韌性規則",
        "regulation_type": "規則",
        "issuing_authority": "FCA",
        "search_keywords": ["FCA operational resilience", "UK financial operational resilience"],
    },
    {
        "name": "Prudential Regulation Authority (PRA) SS1/21 Operational Resilience",
        "name_en": "PRA SS1/21 Operational Resilience",
        "name_zh": "PRA營運韌性監督聲明",
        "regulation_type": "監督聲明",
        "issuing_authority": "PRA",
        "search_keywords": ["PRA operational resilience SS1/21", "PRA SS1 21"],
    },
    {
        "name": "UK GDPR",
        "name_en": "UK General Data Protection Regulation",
        "name_zh": "英國一般資料保護規則",
        "regulation_type": "法規",
        "issuing_authority": "ICO",
        "search_keywords": ["UK GDPR", "UK data protection regulation"],
    },
    {
        "name": "FCA SYSC 13 Operational Risk",
        "name_en": "FCA SYSC 13 Operational Risk",
        "name_zh": "FCA系統與控制手冊第13章營運風險",
        "regulation_type": "規則",
        "issuing_authority": "FCA",
        "search_keywords": ["FCA SYSC 13 operational risk", "FCA operational risk systems controls"],
    },
]

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
    {
        "name": "Kapitalanlageaufsichtliche Anforderungen an die IT (KAIT)",
        "name_en": "Supervisory Requirements for IT in Capital Management Companies (KAIT)",
        "name_zh": "資本管理業 IT 監管要求",
        "regulation_type": "指引",
        "issuing_authority": "BaFin",
        "search_keywords": ["BaFin KAIT", "KAIT Kapitalanlageaufsichtliche"],
    },
]

FRANCE_REGULATIONS = [
    {
        "name": "Règlement Général sur la Protection des Données (RGPD)",
        "name_en": "General Data Protection Regulation (GDPR)",
        "name_zh": "一般資料保護規則",
        "regulation_type": "規則",
        "issuing_authority": "CNIL",
        "search_keywords": ["France RGPD", "CNIL data protection"],
    },
    {
        "name": "ACPR Guidelines on IT System Security",
        "name_en": "ACPR Guidelines on IT System Security",
        "name_zh": "ACPR資訊系統安全指引",
        "regulation_type": "指引",
        "issuing_authority": "ACPR",
        "search_keywords": ["ACPR IT security guidelines", "ACPR system security"],
    },
    {
        "name": "Loi de programmation militaire (LPM) - Cybersecurity Provisions",
        "name_en": "Military Programming Law - Cybersecurity",
        "name_zh": "軍事規劃法網路安全條款",
        "regulation_type": "法律",
        "issuing_authority": "ANSSI",
        "search_keywords": ["France LPM cybersecurity", "ANSSI critical infrastructure"],
    },
]

SWITZERLAND_REGULATIONS = [
    {
        "name": "FINMA Circular 2023/1 Operational Risks and Resilience",
        "name_en": "FINMA Circular on Operational Risks and Resilience",
        "name_zh": "FINMA營運風險與韌性通報",
        "regulation_type": "通報",
        "issuing_authority": "FINMA",
        "search_keywords": ["FINMA operational risk circular", "FINMA 2023/1 resilience"],
    },
    {
        "name": "Swiss Federal Act on Data Protection (FADP)",
        "name_en": "Federal Act on Data Protection (FADP)",
        "name_zh": "聯邦資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "FDPIC",
        "search_keywords": ["Switzerland FADP", "Swiss data protection act nDSG"],
    },
    {
        "name": "FINMA Circular 2008/21 Operational Risks Banks",
        "name_en": "FINMA Circular on Operational Risks Banks",
        "name_zh": "FINMA銀行營運風險通報",
        "regulation_type": "通報",
        "issuing_authority": "FINMA",
        "search_keywords": ["FINMA 2008/21 operational risk", "FINMA banks operational"],
    },
]


# ============================================================
# 北美地區
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
    {
        "name": "SEC Cybersecurity Risk Management Rule",
        "name_en": "SEC Cybersecurity Risk Management Rule",
        "name_zh": "SEC網路安全風險管理規則",
        "regulation_type": "規則",
        "issuing_authority": "SEC",
        "search_keywords": ["SEC cybersecurity rule", "SEC cyber risk management"],
    },
    {
        "name": "California Consumer Privacy Act (CCPA)",
        "name_en": "California Consumer Privacy Act (CCPA)",
        "name_zh": "加州消費者隱私法",
        "regulation_type": "法律",
        "issuing_authority": "State of California",
        "search_keywords": ["CCPA", "California Consumer Privacy Act"],
    },
]

CANADA_REGULATIONS = [
    {
        "name": "Personal Information Protection and Electronic Documents Act (PIPEDA)",
        "name_en": "Personal Information Protection and Electronic Documents Act",
        "name_zh": "個人資訊保護及電子文件法",
        "regulation_type": "法律",
        "issuing_authority": "Government of Canada",
        "search_keywords": ["PIPEDA Canada", "Canada personal information protection"],
    },
    {
        "name": "OSFI Guideline B-13 Technology and Cyber Risk Management",
        "name_en": "OSFI B-13 Technology and Cyber Risk Management",
        "name_zh": "OSFI技術與網路風險管理指引",
        "regulation_type": "指引",
        "issuing_authority": "OSFI",
        "search_keywords": ["OSFI B-13", "OSFI technology cyber risk"],
    },
    {
        "name": "OSFI Guideline B-10 Outsourcing of Business Activities",
        "name_en": "OSFI B-10 Outsourcing",
        "name_zh": "OSFI業務活動委外指引",
        "regulation_type": "指引",
        "issuing_authority": "OSFI",
        "search_keywords": ["OSFI B-10 outsourcing", "OSFI outsourcing guideline"],
    },
]

MEXICO_REGULATIONS = [
    {
        "name": "Ley Federal de Protección de Datos Personales en Posesión de los Particulares",
        "name_en": "Federal Law on Protection of Personal Data Held by Private Parties",
        "name_zh": "私人持有個人資料保護聯邦法",
        "regulation_type": "法律",
        "issuing_authority": "INAI",
        "search_keywords": ["Mexico LFPDPPP", "Mexico personal data protection law"],
    },
    {
        "name": "Disposiciones de Carácter General Aplicables a las Instituciones de Crédito - Seguridad de la Información",
        "name_en": "CNBV General Provisions on Information Security",
        "name_zh": "信用機構資訊安全一般規定",
        "regulation_type": "規定",
        "issuing_authority": "CNBV",
        "search_keywords": ["CNBV information security", "Mexico banking cybersecurity"],
    },
]


# ============================================================
# 南美地區
# ============================================================

BRAZIL_REGULATIONS = [
    {
        "name": "Lei Geral de Proteção de Dados (LGPD)",
        "name_en": "General Data Protection Law (LGPD)",
        "name_zh": "一般資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "ANPD",
        "search_keywords": ["Brazil LGPD", "Lei Geral Proteção Dados"],
    },
    {
        "name": "Resolução CMN 4.893 - Política de Segurança Cibernética",
        "name_en": "CMN Resolution 4893 on Cybersecurity Policy",
        "name_zh": "CMN網路安全政策決議",
        "regulation_type": "決議",
        "issuing_authority": "BCB",
        "search_keywords": ["Resolução 4893 cybersecurity", "BCB segurança cibernética"],
    },
    {
        "name": "Resolução BCB 85 - Segurança Cibernética",
        "name_en": "BCB Resolution 85 on Cybersecurity",
        "name_zh": "巴西央行網路安全決議",
        "regulation_type": "決議",
        "issuing_authority": "BCB",
        "search_keywords": ["BCB Resolution 85", "Banco Central cybersecurity"],
    },
]

ARGENTINA_REGULATIONS = [
    {
        "name": "Ley de Protección de los Datos Personales (Ley 25.326)",
        "name_en": "Personal Data Protection Law",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "AAIP",
        "search_keywords": ["Argentina data protection law 25326", "Ley 25.326"],
    },
    {
        "name": "Comunicación BCRA A 6375 - Requisitos Mínimos de Gestión",
        "name_en": "BCRA Communication on Minimum Management Requirements",
        "name_zh": "阿根廷央行最低管理要求通報",
        "regulation_type": "通報",
        "issuing_authority": "BCRA",
        "search_keywords": ["BCRA A 6375", "BCRA minimum requirements IT"],
    },
]

CHILE_REGULATIONS = [
    {
        "name": "Ley de Protección de Datos Personales (Ley 19.628)",
        "name_en": "Personal Data Protection Law",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "Government of Chile",
        "search_keywords": ["Chile data protection law 19628", "Ley 19.628"],
    },
    {
        "name": "CMF Norma de Carácter General sobre Ciberseguridad",
        "name_en": "CMF General Norm on Cybersecurity",
        "name_zh": "CMF網路安全一般規範",
        "regulation_type": "規範",
        "issuing_authority": "CMF",
        "search_keywords": ["CMF Chile cybersecurity", "CMF norma ciberseguridad"],
    },
]


# ============================================================
# 大洋洲地區
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
    {
        "name": "Security of Critical Infrastructure Act 2018 (SOCI)",
        "name_en": "Security of Critical Infrastructure Act",
        "name_zh": "關鍵基礎設施安全法",
        "regulation_type": "法律",
        "issuing_authority": "Australian Government",
        "search_keywords": ["Australia SOCI Act", "Security Critical Infrastructure Act"],
    },
]

NEWZEALAND_REGULATIONS = [
    {
        "name": "Privacy Act 2020",
        "name_en": "Privacy Act 2020",
        "name_zh": "隱私法",
        "regulation_type": "法律",
        "issuing_authority": "Government of New Zealand",
        "search_keywords": ["New Zealand Privacy Act 2020", "NZ privacy law"],
    },
    {
        "name": "Reserve Bank Guidance on Cyber Resilience",
        "name_en": "RBNZ Guidance on Cyber Resilience",
        "name_zh": "紐西蘭央行網路韌性指引",
        "regulation_type": "指引",
        "issuing_authority": "RBNZ",
        "search_keywords": ["RBNZ cyber resilience", "Reserve Bank NZ cybersecurity"],
    },
]


# ============================================================
# 非洲地區
# ============================================================

SOUTHAFRICA_REGULATIONS = [
    {
        "name": "Protection of Personal Information Act (POPIA)",
        "name_en": "Protection of Personal Information Act",
        "name_zh": "個人資訊保護法",
        "regulation_type": "法律",
        "issuing_authority": "Information Regulator",
        "search_keywords": ["South Africa POPIA", "Protection Personal Information Act"],
    },
    {
        "name": "Cybercrimes Act",
        "name_en": "Cybercrimes Act",
        "name_zh": "網路犯罪法",
        "regulation_type": "法律",
        "issuing_authority": "Government of South Africa",
        "search_keywords": ["South Africa Cybercrimes Act", "SA cyber crimes law"],
    },
    {
        "name": "SARB Guidance Note on Cybersecurity",
        "name_en": "SARB Guidance on Cybersecurity",
        "name_zh": "南非央行網路安全指引",
        "regulation_type": "指引",
        "issuing_authority": "SARB",
        "search_keywords": ["SARB cybersecurity guidance", "South Africa Reserve Bank cyber"],
    },
]

NIGERIA_REGULATIONS = [
    {
        "name": "Nigeria Data Protection Regulation (NDPR)",
        "name_en": "Nigeria Data Protection Regulation",
        "name_zh": "奈及利亞資料保護規則",
        "regulation_type": "規則",
        "issuing_authority": "NITDA",
        "search_keywords": ["Nigeria NDPR", "Nigeria Data Protection Regulation"],
    },
    {
        "name": "CBN Risk-Based Cybersecurity Framework",
        "name_en": "CBN Risk-Based Cybersecurity Framework",
        "name_zh": "奈及利亞央行風險導向網路安全框架",
        "regulation_type": "框架",
        "issuing_authority": "CBN",
        "search_keywords": ["CBN cybersecurity framework", "Central Bank Nigeria cyber"],
    },
]

KENYA_REGULATIONS = [
    {
        "name": "Data Protection Act, 2019",
        "name_en": "Data Protection Act, 2019",
        "name_zh": "資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "ODPC",
        "search_keywords": ["Kenya Data Protection Act 2019", "Kenya DPA"],
    },
    {
        "name": "CBK Guidance Note on Cybersecurity",
        "name_en": "CBK Guidance on Cybersecurity",
        "name_zh": "肯亞央行網路安全指引",
        "regulation_type": "指引",
        "issuing_authority": "CBK",
        "search_keywords": ["CBK cybersecurity guidance", "Central Bank Kenya cyber"],
    },
]

EGYPT_REGULATIONS = [
    {
        "name": "Personal Data Protection Law",
        "name_en": "Egypt Personal Data Protection Law",
        "name_zh": "個人資料保護法",
        "regulation_type": "法律",
        "issuing_authority": "Government of Egypt",
        "search_keywords": ["Egypt data protection law", "Egypt personal data protection"],
    },
    {
        "name": "CBE Cybersecurity Framework",
        "name_en": "CBE Cybersecurity Framework",
        "name_zh": "埃及央行網路安全框架",
        "regulation_type": "框架",
        "issuing_authority": "CBE",
        "search_keywords": ["CBE cybersecurity framework", "Central Bank Egypt cyber"],
    },
]


# ============================================================
# 匯入函數
# ============================================================

ALL_REGULATIONS_MAP = {
    # 東亞
    "JP": ("finance_general", "cybersecurity", JAPAN_REGULATIONS),
    "KR": ("finance_general", "cybersecurity", KOREA_REGULATIONS),
    "TW": ("finance_general", "cybersecurity", TAIWAN_REGULATIONS),
    "CN": ("finance_general", "cybersecurity", CHINA_REGULATIONS),
    "HK": ("finance_general", "cybersecurity", HONGKONG_REGULATIONS),
    # 東南亞
    "SG": ("finance_general", "cybersecurity", SINGAPORE_REGULATIONS),
    "MY": ("finance_general", "cybersecurity", MALAYSIA_REGULATIONS),
    "TH": ("finance_general", "cybersecurity", THAILAND_REGULATIONS),
    "ID": ("finance_general", "cybersecurity", INDONESIA_REGULATIONS),
    "VN": ("finance_general", "cybersecurity", VIETNAM_REGULATIONS),
    "PH": ("finance_general", "cybersecurity", PHILIPPINES_REGULATIONS),
    # 南亞
    "IN": ("finance_general", "cybersecurity", INDIA_REGULATIONS),
    # 中東
    "AE": ("finance_general", "cybersecurity", UAE_REGULATIONS),
    "SA": ("finance_general", "cybersecurity", SAUDI_REGULATIONS),
    "IL": ("finance_general", "cybersecurity", ISRAEL_REGULATIONS),
    "TR": ("finance_general", "cybersecurity", TURKEY_REGULATIONS),
    # 歐洲
    "EU": ("finance_general", "cybersecurity", EU_REGULATIONS),
    "GB": ("finance_general", "cybersecurity", UK_REGULATIONS),
    "DE": ("finance_general", "cybersecurity", GERMANY_REGULATIONS),
    "FR": ("finance_general", "cybersecurity", FRANCE_REGULATIONS),
    "CH": ("finance_general", "cybersecurity", SWITZERLAND_REGULATIONS),
    # 北美
    "US": ("finance_general", "cybersecurity", US_REGULATIONS),
    "CA": ("finance_general", "cybersecurity", CANADA_REGULATIONS),
    "MX": ("finance_general", "cybersecurity", MEXICO_REGULATIONS),
    # 南美
    "BR": ("finance_general", "cybersecurity", BRAZIL_REGULATIONS),
    "AR": ("finance_general", "cybersecurity", ARGENTINA_REGULATIONS),
    "CL": ("finance_general", "cybersecurity", CHILE_REGULATIONS),
    # 大洋洲
    "AU": ("finance_general", "cybersecurity", AUSTRALIA_REGULATIONS),
    "NZ": ("finance_general", "cybersecurity", NEWZEALAND_REGULATIONS),
    # 非洲
    "ZA": ("finance_general", "cybersecurity", SOUTHAFRICA_REGULATIONS),
    "NG": ("finance_general", "cybersecurity", NIGERIA_REGULATIONS),
    "KE": ("finance_general", "cybersecurity", KENYA_REGULATIONS),
    "EG": ("finance_general", "cybersecurity", EGYPT_REGULATIONS),
}


def seed_all_regulations():
    """匯入所有國家的必搜法規"""
    print("=" * 60)
    print("[Seed] 開始匯入完整版必搜法規...")
    print("=" * 60)

    manager = BaselineManager()
    total_count = 0
    country_counts = {}

    for country_code, (industry_code, topic_code, regulations) in ALL_REGULATIONS_MAP.items():
        print(f"\n[{country_code}] 匯入 {len(regulations)} 筆法規...")
        country_counts[country_code] = 0

        for reg in regulations:
            try:
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
                country_counts[country_code] += 1
            except Exception as e:
                print(f"  [錯誤] {reg['name']}: {e}")

    print("\n" + "=" * 60)
    print(f"[Seed] 匯入完成! 共 {total_count} 筆必搜法規")
    print("=" * 60)

    # 顯示統計
    stats = manager.get_statistics()
    print(f"\n=== 統計 ===")
    print(f"法規總數: {stats['total']} 筆")
    print(f"必搜法規: {stats['mandatory']} 筆")

    print(f"\n=== 按國家 ===")
    for country, count in sorted(stats["by_country"].items(), key=lambda x: -x[1]):
        print(f"  {country}: {count} 筆")

    manager.close()
    return total_count


if __name__ == "__main__":
    seed_all_regulations()
