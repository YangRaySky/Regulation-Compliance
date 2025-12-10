"""
查詢歷史記錄模組

提供查詢歷史的持久化儲存功能：
- 自動儲存成功的查詢結果
- 列出歷史記錄
- 載入特定歷史項目
- 刪除歷史項目
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4


class QueryHistory:
    """查詢歷史記錄管理器"""

    def __init__(self, history_file: str = ".data/history.json", max_items: int = 50):
        """
        初始化歷史記錄管理器

        Args:
            history_file: 歷史記錄檔案路徑
            max_items: 最大保留項目數
        """
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.max_items = max_items

    def _load(self) -> list[dict]:
        """載入歷史記錄"""
        if not self.history_file.exists():
            return []

        try:
            data = json.loads(self.history_file.read_text(encoding='utf-8'))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, ValueError):
            return []

    def _save(self, history: list[dict]):
        """儲存歷史記錄"""
        self.history_file.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def add(self, query: str, result: dict) -> str:
        """
        新增歷史記錄

        Args:
            query: 查詢字串
            result: 查詢結果

        Returns:
            歷史記錄 ID
        """
        history = self._load()

        # 提取原始查詢（不含用戶補充說明）
        original_query = query.split("\n\n【用戶補充說明】")[0].strip()

        # 建立歷史項目
        item_id = str(uuid4())[:8]
        item = {
            'id': item_id,
            'timestamp': datetime.now().isoformat(),
            'query': original_query,
            'full_query': query,
            'result': result,
        }

        # 新增到最前面
        history.insert(0, item)

        # 限制數量
        if len(history) > self.max_items:
            history = history[:self.max_items]

        self._save(history)
        return item_id

    def list_all(self) -> list[dict]:
        """
        列出所有歷史記錄（摘要）

        Returns:
            歷史記錄摘要列表
        """
        history = self._load()

        summaries = []
        for item in history:
            # 計算時間差
            try:
                item_time = datetime.fromisoformat(item['timestamp'])
                age_minutes = int((datetime.now() - item_time).total_seconds() / 60)
            except (KeyError, ValueError):
                age_minutes = 0

            # 計算法規數量
            regulations = item.get('result', {}).get('regulations', {})
            if isinstance(regulations, dict):
                reg_count = len(regulations.get('verified_regulations', []))
            elif isinstance(regulations, list):
                reg_count = len(regulations)
            else:
                reg_count = 0

            summaries.append({
                'id': item.get('id', ''),
                'query': item.get('query', '')[:40],
                'timestamp': item.get('timestamp', ''),
                'age_minutes': age_minutes,
                'reg_count': reg_count,
            })

        return summaries

    def get(self, item_id: str) -> Optional[dict]:
        """
        取得特定歷史記錄

        Args:
            item_id: 歷史記錄 ID

        Returns:
            完整的歷史記錄項目
        """
        history = self._load()

        for item in history:
            if item.get('id') == item_id:
                return item

        return None

    def delete(self, item_id: str) -> bool:
        """
        刪除特定歷史記錄

        Args:
            item_id: 歷史記錄 ID

        Returns:
            是否成功刪除
        """
        history = self._load()
        original_len = len(history)

        history = [item for item in history if item.get('id') != item_id]

        if len(history) < original_len:
            self._save(history)
            return True

        return False

    def clear_all(self) -> int:
        """
        清空所有歷史記錄

        Returns:
            刪除的項目數量
        """
        history = self._load()
        count = len(history)
        self._save([])
        return count


# 全域歷史記錄實例
_history_instance: Optional[QueryHistory] = None


def get_history() -> QueryHistory:
    """取得全域歷史記錄實例"""
    global _history_instance
    if _history_instance is None:
        _history_instance = QueryHistory()
    return _history_instance
