"""
查詢結果快取模組

提供查詢結果的本地檔案快取功能，支援：
- 自動過期（TTL）
- 列出所有快取
- 刪除單一快取
- 清空全部快取
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class QueryCache:
    """查詢結果快取管理器"""

    def __init__(self, cache_dir: str = ".cache/queries", ttl_hours: int = 24):
        """
        初始化快取管理器

        Args:
            cache_dir: 快取目錄路徑
            ttl_hours: 快取有效期（小時）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _make_key(self, query: str, jurisdiction: str) -> str:
        """生成快取鍵值"""
        combined = f"{query}|{jurisdiction}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:16]

    def get(self, query: str, jurisdiction: str) -> Optional[dict]:
        """
        取得快取結果

        Args:
            query: 查詢字串
            jurisdiction: 目標地區

        Returns:
            快取的結果，若不存在或已過期則返回 None
        """
        key = self._make_key(query, jurisdiction)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            cached_time = datetime.fromisoformat(data['timestamp'])

            # 檢查是否過期
            if datetime.now() - cached_time > self.ttl:
                # 過期，刪除並返回 None
                cache_file.unlink()
                return None

            return data['result']
        except (json.JSONDecodeError, KeyError, ValueError):
            # 快取檔案損壞，刪除
            cache_file.unlink()
            return None

    def set(self, query: str, jurisdiction: str, result: dict) -> str:
        """
        儲存快取結果

        Args:
            query: 查詢字串
            jurisdiction: 目標地區
            result: 查詢結果

        Returns:
            快取 ID
        """
        key = self._make_key(query, jurisdiction)
        cache_file = self.cache_dir / f"{key}.json"

        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'jurisdiction': jurisdiction,
            'result': result
        }

        cache_file.write_text(
            json.dumps(cache_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        return key

    def list_all(self) -> list[dict]:
        """
        列出所有快取項目

        Returns:
            快取項目列表，包含 id、query、timestamp、size
        """
        items = []

        for f in self.cache_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
                cached_time = datetime.fromisoformat(data['timestamp'])

                # 檢查是否過期
                if datetime.now() - cached_time > self.ttl:
                    # 過期，刪除
                    f.unlink()
                    continue

                items.append({
                    'id': f.stem,
                    'query': data.get('query', '未知查詢'),
                    'jurisdiction': data.get('jurisdiction', ''),
                    'timestamp': data.get('timestamp'),
                    'size': f.stat().st_size,
                    'age_minutes': int((datetime.now() - cached_time).total_seconds() / 60)
                })
            except (json.JSONDecodeError, KeyError, ValueError):
                # 損壞的快取檔案，刪除
                f.unlink()
                continue

        # 按時間排序，最新的在前
        return sorted(items, key=lambda x: x['timestamp'], reverse=True)

    def delete(self, cache_id: str) -> bool:
        """
        刪除單一快取

        Args:
            cache_id: 快取 ID

        Returns:
            是否成功刪除
        """
        cache_file = self.cache_dir / f"{cache_id}.json"

        if cache_file.exists():
            cache_file.unlink()
            return True

        return False

    def clear_all(self) -> int:
        """
        清空所有快取

        Returns:
            刪除的快取數量
        """
        count = 0

        for f in self.cache_dir.glob("*.json"):
            f.unlink()
            count += 1

        return count

    def get_stats(self) -> dict:
        """
        取得快取統計資訊

        Returns:
            包含 total_count、total_size、oldest、newest 的字典
        """
        items = self.list_all()

        if not items:
            return {
                'total_count': 0,
                'total_size': 0,
                'oldest': None,
                'newest': None
            }

        total_size = sum(item['size'] for item in items)

        return {
            'total_count': len(items),
            'total_size': total_size,
            'total_size_kb': round(total_size / 1024, 2),
            'oldest': items[-1]['timestamp'] if items else None,
            'newest': items[0]['timestamp'] if items else None
        }


# 全域快取實例
_cache_instance: Optional[QueryCache] = None


def get_cache() -> QueryCache:
    """取得全域快取實例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = QueryCache()
    return _cache_instance
