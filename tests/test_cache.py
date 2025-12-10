"""
快取模組單元測試

測試 src/utils/cache.py 的功能。
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

from src.utils.cache import QueryCache


class TestQueryCache:
    """QueryCache 類別測試"""

    def test_init_creates_directory(self, temp_dir):
        """測試初始化時建立快取目錄"""
        cache_dir = temp_dir / "test_cache"
        cache = QueryCache(cache_dir=str(cache_dir), ttl_hours=1)

        assert cache_dir.exists()
        assert cache_dir.is_dir()

    def test_set_and_get(self, temp_dir):
        """測試寫入和讀取快取"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=1)

        query = "測試查詢"
        jurisdiction = "TW"
        result = {"status": "success", "data": "測試資料"}

        # 寫入快取
        cache_id = cache.set(query, jurisdiction, result)
        assert cache_id is not None
        assert len(cache_id) == 16  # SHA256 前 16 字元

        # 讀取快取
        cached = cache.get(query, jurisdiction)
        assert cached is not None
        assert cached["status"] == "success"
        assert cached["data"] == "測試資料"

    def test_get_nonexistent(self, temp_dir):
        """測試讀取不存在的快取"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=1)

        result = cache.get("不存在的查詢", "TW")
        assert result is None

    def test_get_expired(self, temp_dir):
        """測試讀取已過期的快取"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=0)  # 0 小時 = 立即過期

        query = "測試查詢"
        jurisdiction = "TW"
        result = {"status": "success"}

        # 寫入快取
        cache.set(query, jurisdiction, result)

        # 手動修改時間戳記使其過期
        cache_key = cache._make_key(query, jurisdiction)
        cache_file = Path(temp_dir) / f"{cache_key}.json"

        data = json.loads(cache_file.read_text(encoding='utf-8'))
        data['timestamp'] = (datetime.now() - timedelta(hours=2)).isoformat()
        cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

        # 讀取應返回 None（已過期）
        cached = cache.get(query, jurisdiction)
        assert cached is None

    def test_delete(self, temp_dir):
        """測試刪除單一快取"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=1)

        query = "測試查詢"
        jurisdiction = "TW"
        result = {"status": "success"}

        # 寫入快取
        cache_id = cache.set(query, jurisdiction, result)

        # 確認存在
        assert cache.get(query, jurisdiction) is not None

        # 刪除
        deleted = cache.delete(cache_id)
        assert deleted is True

        # 確認已刪除
        assert cache.get(query, jurisdiction) is None

    def test_delete_nonexistent(self, temp_dir):
        """測試刪除不存在的快取"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=1)

        deleted = cache.delete("nonexistent_id")
        assert deleted is False

    def test_clear_all(self, temp_dir):
        """測試清空所有快取"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=1)

        # 寫入多個快取
        cache.set("查詢1", "TW", {"data": 1})
        cache.set("查詢2", "TW", {"data": 2})
        cache.set("查詢3", "JP", {"data": 3})

        # 清空
        count = cache.clear_all()
        assert count == 3

        # 確認已清空
        assert cache.get("查詢1", "TW") is None
        assert cache.get("查詢2", "TW") is None
        assert cache.get("查詢3", "JP") is None

    def test_list_all(self, temp_dir):
        """測試列出所有快取"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=1)

        # 寫入多個快取
        cache.set("查詢1", "TW", {"data": 1})
        cache.set("查詢2", "TW", {"data": 2})

        # 列出
        items = cache.list_all()
        assert len(items) == 2

        # 檢查結構
        for item in items:
            assert 'id' in item
            assert 'query' in item
            assert 'jurisdiction' in item
            assert 'timestamp' in item
            assert 'size' in item
            assert 'age_minutes' in item

    def test_list_all_sorted_by_time(self, temp_dir):
        """測試列出快取按時間排序（最新在前）"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=1)

        # 寫入多個快取（稍微間隔）
        cache.set("舊查詢", "TW", {"data": 1})
        time.sleep(0.1)
        cache.set("新查詢", "TW", {"data": 2})

        items = cache.list_all()
        assert len(items) == 2
        assert items[0]['query'] == "新查詢"
        assert items[1]['query'] == "舊查詢"

    def test_get_stats(self, temp_dir):
        """測試取得快取統計"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=1)

        # 空快取
        stats = cache.get_stats()
        assert stats['total_count'] == 0
        assert stats['total_size'] == 0

        # 加入資料
        cache.set("查詢1", "TW", {"data": "x" * 100})
        cache.set("查詢2", "TW", {"data": "y" * 200})

        stats = cache.get_stats()
        assert stats['total_count'] == 2
        assert stats['total_size'] > 0
        assert stats['newest'] is not None
        assert stats['oldest'] is not None

    def test_same_query_different_jurisdiction(self, temp_dir):
        """測試相同查詢不同地區產生不同快取"""
        cache = QueryCache(cache_dir=str(temp_dir), ttl_hours=1)

        query = "個資法"

        cache.set(query, "TW", {"region": "台灣"})
        cache.set(query, "JP", {"region": "日本"})

        tw_result = cache.get(query, "TW")
        jp_result = cache.get(query, "JP")

        assert tw_result["region"] == "台灣"
        assert jp_result["region"] == "日本"
