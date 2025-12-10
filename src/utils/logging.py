"""
日誌模組

使用 loguru 提供統一的日誌功能。
"""

import sys
import os
from pathlib import Path

from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "./logs/app.log",
    rotation: str = "10 MB",
    retention: str = "7 days",
) -> None:
    """
    設定日誌系統

    Args:
        log_level: 日誌等級
        log_file: 日誌檔案路徑
        rotation: 日誌輪替大小
        retention: 日誌保留時間
    """
    # 移除預設的 handler
    logger.remove()

    # 取得日誌等級
    level = os.getenv("LOG_LEVEL", log_level).upper()

    # 設定控制台輸出
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
    )

    # 設定檔案輸出
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_file,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
    )

    logger.info(f"日誌系統已初始化 - 等級: {level}")


def get_logger(name: str = None):
    """
    取得 logger 實例

    Args:
        name: logger 名稱（通常使用 __name__）

    Returns:
        logger 實例
    """
    if name:
        return logger.bind(name=name)
    return logger


# 模組載入時自動初始化 (預設關閉以避免載入問題)
# if os.getenv("AUTO_INIT_LOGGING", "false").lower() == "true":
#     setup_logging()
