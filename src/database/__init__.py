"""
資料庫模組

提供:
- 法規 Baseline 資料庫架構
- CRUD 操作與查詢
- 信心度計算與驗證機制
- 定期驗證排程
"""

from .manager import BaselineManager
from .models import (
    Base,
    Country,
    Industry,
    RegulationBaseline,
    Topic,
    VerificationLog,
    get_database_path,
    get_engine,
    get_session,
    init_database,
)
from .seed_data import seed_all
from .verifier import (
    RegulationVerifier,
    run_full_verification,
    run_scheduled_verification,
)

__all__ = [
    # 模型
    "Base",
    "Country",
    "Industry",
    "Topic",
    "RegulationBaseline",
    "VerificationLog",
    # 資料庫函數
    "get_engine",
    "get_session",
    "init_database",
    "get_database_path",
    # 管理工具
    "BaselineManager",
    "seed_all",
    # 驗證工具
    "RegulationVerifier",
    "run_scheduled_verification",
    "run_full_verification",
]
