"""
Pytest 設定檔

提供共用的 fixtures 和測試設定。
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """建立暫存目錄，測試結束後自動清理"""
    dir_path = tempfile.mkdtemp()
    yield Path(dir_path)
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def sample_query_result():
    """範例查詢結果資料"""
    return {
        "status": "success",
        "query": "台灣個人資料保護法",
        "original_query": "台灣個資法",
        "timestamp": "2024-12-01T12:00:00",
        "regulations": {
            "summary": "個人資料保護法是台灣規範個資蒐集、處理及利用的主要法律。",
            "verified_regulations": [
                {
                    "name": "Personal Data Protection Act",
                    "name_zh": "個人資料保護法",
                    "jurisdiction": "台灣",
                    "type": "法律",
                    "url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0050021",
                    "relevance_score": 0.95,
                    "key_points": [
                        "規範個人資料之蒐集、處理及利用",
                        "保障人民之隱私權益",
                        "違反者可處罰鍰或刑責"
                    ],
                    "article_excerpts": [
                        {
                            "article_number": "第 1 條",
                            "title": "立法目的",
                            "content": "為規範個人資料之蒐集、處理及利用，以避免人格權受侵害，並促進個人資料之合理利用，特制定本法。",
                            "relevance": "說明本法立法目的"
                        }
                    ],
                    "notes": "本法於 2015 年大幅修正"
                }
            ],
            "timeline": [
                {
                    "date": "1995-08-11",
                    "event": "電腦處理個人資料保護法公布",
                    "regulation": "個人資料保護法前身"
                },
                {
                    "date": "2010-05-26",
                    "event": "個人資料保護法公布",
                    "regulation": "個人資料保護法"
                }
            ],
            "compliance_checklist": [
                {
                    "item": "告知義務",
                    "description": "蒐集個資前應告知當事人蒐集目的",
                    "regulation_basis": "個資法第 8 條",
                    "priority": "high"
                },
                {
                    "item": "同意取得",
                    "description": "特定目的外利用需取得書面同意",
                    "regulation_basis": "個資法第 16 條",
                    "priority": "high"
                }
            ],
            "confidence_score": 0.92,
            "warnings": ["請注意各行業可能有特別規定"],
            "limitations": ["本分析僅供參考，不構成法律意見"]
        }
    }


@pytest.fixture
def empty_query_result():
    """空的查詢結果資料"""
    return {
        "status": "success",
        "query": "不存在的法規",
        "timestamp": "2024-12-01T12:00:00",
        "regulations": {
            "summary": "",
            "verified_regulations": [],
            "timeline": [],
            "compliance_checklist": [],
            "confidence_score": 0
        }
    }


@pytest.fixture
def sample_cache_data():
    """範例快取資料"""
    return {
        "query": "測試查詢",
        "jurisdiction": "TW",
        "result": {
            "status": "success",
            "regulations": []
        }
    }
