"""
更新法規的產業適用性

將現有法規標記為：
1. 跨產業通用法規（如 GDPR、資安法、個資法）
2. 金融業專用法規（如 MAS TRM、DORA）
3. 適用於多個金融子產業（銀行、證券、保險等）
"""

from sqlalchemy import text

from .models import RegulationBaseline, get_session, init_database


def update_industry_applicability():
    """更新所有法規的產業適用性"""

    # 確保新欄位存在
    init_database()

    # 使用 raw SQL 添加新欄位（如果不存在）
    session = get_session()
    try:
        session.execute(text("ALTER TABLE regulation_baselines ADD COLUMN applicable_industries TEXT"))
        session.commit()
        print("✅ 新增 applicable_industries 欄位")
    except Exception:
        session.rollback()

    try:
        session.execute(text("ALTER TABLE regulation_baselines ADD COLUMN is_cross_industry INTEGER DEFAULT 0"))
        session.commit()
        print("✅ 新增 is_cross_industry 欄位")
    except Exception:
        session.rollback()

    session.close()

    # 定義跨產業通用法規的關鍵字
    CROSS_INDUSTRY_KEYWORDS = [
        # 個資/隱私法規
        'GDPR', 'PDPA', 'POPIA', 'LGPD', 'PIPEDA', 'CCPA', 'Privacy',
        '個人資料保護', '個人情報保護', '개인정보', '个人信息保护',
        'Data Protection', 'Datenschutz', '隱私', '隐私',
        # 資安法規
        'Cybersecurity Act', 'Cybercrimes', '資通安全管理法', '网络安全法',
        'サイバーセキュリティ基本法', 'NIS2', 'NIST',
        # 資訊科技法規
        'Information Technology Act', 'IT Act',
    ]

    # 定義金融業專用法規的關鍵字
    FINANCE_SPECIFIC_KEYWORDS = [
        'MAS', 'HKMA', 'APRA', 'FCA', 'PRA', 'SEC', 'FINMA', 'BaFin',
        'OSFI', 'OJK', 'BNM', 'BOT', 'BSP', 'RBI', 'SAMA', 'CBUAE',
        'Banking', 'Bank', '銀行', '金融', 'Financial',
        'Insurance', '保険', '保險', 'Securities', '証券', '證券',
        'DORA', 'CPS 234', 'CPS 230', 'B-13', 'B-10',
        '電子金融', '전자금융',
    ]

    # 金融子產業對應
    FINANCE_SUB_INDUSTRIES = ['banking', 'securities', 'insurance', 'fintech', 'finance_general']

    session = get_session()
    regulations = session.query(RegulationBaseline).all()

    updated_count = 0
    cross_industry_count = 0
    finance_specific_count = 0

    for reg in regulations:
        name_combined = f"{reg.name} {reg.name_en or ''} {reg.name_zh or ''}"

        # 檢查是否為跨產業法規
        is_cross = any(kw.lower() in name_combined.lower() for kw in CROSS_INDUSTRY_KEYWORDS)

        if is_cross:
            # 跨產業通用法規 - 適用於所有產業
            reg.is_cross_industry = True
            reg.applicable_industries = [
                'banking', 'securities', 'insurance', 'fintech', 'finance_general',
                'healthcare', 'technology', 'telecom', 'ecommerce', 'manufacturing',
                'energy', 'retail', 'logistics', 'education', 'government'
            ]
            cross_industry_count += 1
        else:
            # 金融業專用法規
            is_finance = any(kw.lower() in name_combined.lower() for kw in FINANCE_SPECIFIC_KEYWORDS)

            if is_finance:
                reg.is_cross_industry = False
                reg.applicable_industries = FINANCE_SUB_INDUSTRIES
                finance_specific_count += 1
            else:
                # 預設為金融業
                reg.is_cross_industry = False
                reg.applicable_industries = FINANCE_SUB_INDUSTRIES

        updated_count += 1

    session.commit()
    session.close()

    print("\n=== 更新完成 ===")
    print(f"總更新數: {updated_count}")
    print(f"跨產業通用法規: {cross_industry_count}")
    print(f"金融業專用法規: {finance_specific_count}")


def print_summary():
    """顯示產業適用性統計"""
    session = get_session()
    regulations = session.query(RegulationBaseline).all()

    cross_industry = [r for r in regulations if r.is_cross_industry]
    finance_only = [r for r in regulations if not r.is_cross_industry]

    print("\n=== 產業適用性統計 ===")
    print(f"跨產業通用法規: {len(cross_industry)} 筆")
    print(f"金融業專用法規: {len(finance_only)} 筆")

    print("\n--- 跨產業通用法規範例 ---")
    for r in cross_industry[:5]:
        print(f"  [{r.country_code}] {r.name[:40]}...")

    print("\n--- 金融業專用法規範例 ---")
    for r in finance_only[:5]:
        print(f"  [{r.country_code}] {r.name[:40]}...")

    session.close()


if __name__ == "__main__":
    update_industry_applicability()
    print_summary()
