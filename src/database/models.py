"""
法規 Baseline 資料庫模型

使用 SQLite + SQLAlchemy 管理法規基準清單
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    Index,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

Base = declarative_base()


class Country(Base):
    """國家/地區表"""
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)  # 如: TW, JP, US
    name_zh = Column(String(50), nullable=False)  # 中文名稱
    name_en = Column(String(50), nullable=False)  # 英文名稱
    region = Column(String(50))  # 區域: 東亞、東南亞、歐洲...
    search_config = Column(JSON)  # Google Custom Search 設定
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Industry(Base):
    """產業別表"""
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # 如: finance, healthcare
    name_zh = Column(String(100), nullable=False)  # 中文名稱
    name_en = Column(String(100), nullable=False)  # 英文名稱
    category = Column(String(50))  # 大類: 金融、科技、製造...
    description = Column(Text)  # 描述
    keywords = Column(JSON)  # 相關搜尋關鍵字
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Topic(Base):
    """法規主題表"""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # 如: cybersecurity, privacy
    name_zh = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    description = Column(Text)
    keywords = Column(JSON)  # 各語言的搜尋關鍵字
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RegulationBaseline(Base):
    """法規 Baseline 主表"""
    __tablename__ = "regulation_baselines"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # === 基本資訊 ===
    name = Column(String(500), nullable=False)  # 原文名稱
    name_en = Column(String(500))  # 英文名稱
    name_zh = Column(String(500))  # 中文名稱

    # === 分類 ===
    country_code = Column(String(10), nullable=False)  # 國家代碼
    industry_code = Column(String(50), nullable=False)  # 主要產業代碼
    topic_code = Column(String(50), nullable=False)  # 主題代碼

    # === 產業適用性 ===
    applicable_industries = Column(JSON)  # 適用產業列表，如 ["banking", "insurance", "fintech"]
    is_cross_industry = Column(Boolean, default=False)  # 是否為跨產業通用法規（如個資法、資安法）

    # === 法規資訊 ===
    regulation_type = Column(String(50))  # 類型: 法律、指引、規則...
    issuing_authority = Column(String(200))  # 發布機關
    official_url = Column(String(1000))  # 官方連結
    effective_date = Column(String(20))  # 生效日期
    last_amended = Column(String(20))  # 最後修訂日期

    # === 搜尋設定 ===
    search_keywords = Column(JSON)  # 搜尋關鍵字列表
    search_priority = Column(Integer, default=1)  # 搜尋優先級 (1=最高)

    # === 信心度與驗證 ===
    confidence_score = Column(Float, default=0.5)  # 信心度 0-1
    is_verified = Column(Boolean, default=False)  # 是否經人工驗證
    is_active = Column(Boolean, default=True)  # 是否仍有效
    is_mandatory = Column(Boolean, default=False)  # 是否為必搜法規

    # === 驗證記錄 ===
    last_verified_at = Column(DateTime)  # 上次驗證時間
    last_found_at = Column(DateTime)  # 上次搜尋到的時間
    found_count = Column(Integer, default=0)  # 被搜尋到的次數
    not_found_count = Column(Integer, default=0)  # 未搜尋到的次數
    verification_notes = Column(Text)  # 驗證備註

    # === 元資料 ===
    source = Column(String(100))  # 資料來源: manual, deep_research, search
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # === 索引 ===
    __table_args__ = (
        Index('idx_country_industry_topic', 'country_code', 'industry_code', 'topic_code'),
        Index('idx_confidence', 'confidence_score'),
        Index('idx_is_mandatory', 'is_mandatory'),
        UniqueConstraint('name', 'country_code', 'industry_code', name='uq_regulation'),
    )


class VerificationLog(Base):
    """驗證記錄表"""
    __tablename__ = "verification_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    regulation_id = Column(Integer, nullable=False)  # 關聯 RegulationBaseline.id

    verification_type = Column(String(50))  # 驗證類型: search, manual, scheduled
    was_found = Column(Boolean)  # 是否找到
    search_query = Column(String(500))  # 使用的搜尋關鍵字
    search_results_count = Column(Integer)  # 搜尋結果數
    url_accessible = Column(Boolean)  # URL 是否可存取

    old_confidence = Column(Float)  # 驗證前信心度
    new_confidence = Column(Float)  # 驗證後信心度

    notes = Column(Text)  # 備註
    verified_by = Column(String(100))  # 驗證者 (system/username)
    verified_at = Column(DateTime, default=datetime.utcnow)


# === 資料庫初始化 ===

def get_database_path() -> Path:
    """取得資料庫檔案路徑"""
    db_dir = Path(__file__).parent.parent.parent / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "regulation_baseline.db"


def get_engine():
    """取得資料庫引擎"""
    db_path = get_database_path()
    return create_engine(f"sqlite:///{db_path}", echo=False)


def get_session():
    """取得資料庫 Session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_database():
    """初始化資料庫（建立所有表）"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print(f"[Database] 資料庫已初始化: {get_database_path()}")
    return engine
