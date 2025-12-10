"""
工具 JSON Schema 定義

為 Function Calling 提供工具的結構化定義。
依據 OpenAI Function Calling 規範：https://platform.openai.com/docs/guides/function-calling

格式說明：
- 外層 type 必須為 "function"
- 工具定義必須在 "function" 物件內
- LangChain bind_tools() 會自動處理此格式

注意：
- 不使用 strict: True，因為 strict mode 要求 required 必須包含所有 properties
- 我們的工具有可選參數（如 region, num_results），因此不使用 strict mode
"""

# 工具 JSON Schema 定義
# 依據 OpenAI Function Calling 文檔格式
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": """使用 Google Custom Search API 搜尋法規相關資訊。適用於全球 40+ 國家/地區的法規搜尋。

支援的地區：
- 東亞：台灣、日本、韓國、中國、香港、澳門
- 東南亞：新加坡、馬來西亞、泰國、印尼、越南、菲律賓
- 南亞：印度、巴基斯坦、孟加拉
- 中東：阿聯酋、沙烏地阿拉伯、以色列、土耳其
- 歐洲：歐盟、英國、德國、法國、義大利、西班牙、荷蘭、瑞士、瑞典、波蘭、俄羅斯
- 北美：美國、加拿大、墨西哥
- 南美：巴西、阿根廷、智利、哥倫比亞
- 大洋洲：澳洲、紐西蘭
- 非洲：南非、奈及利亞、肯亞、埃及

進階功能：
- 支援時間限制（最近 1 年、6 個月、2 週等）
- 支援檔案類型過濾（PDF、DOC 等）
- 支援精確詞彙匹配與排除
- 支援 OR 搜尋（至少包含其中一個詞彙）
- 支援按日期排序（找最新法規）""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜尋關鍵字，建議使用當地語言（如日文、韓文、泰文）以獲得更好的結果"
                    },
                    "region": {
                        "type": "string",
                        "enum": [
                            "全球",
                            "台灣", "日本", "韓國", "中國", "香港", "澳門",
                            "新加坡", "馬來西亞", "泰國", "印尼", "越南", "菲律賓",
                            "印度", "巴基斯坦", "孟加拉",
                            "阿聯酋", "沙烏地阿拉伯", "以色列", "土耳其",
                            "歐盟", "英國", "德國", "法國", "義大利", "西班牙", "荷蘭", "瑞士", "瑞典", "波蘭", "俄羅斯",
                            "美國", "加拿大", "墨西哥",
                            "巴西", "阿根廷", "智利", "哥倫比亞",
                            "澳洲", "紐西蘭",
                            "南非", "奈及利亞", "肯亞", "埃及"
                        ],
                        "description": "目標地區，會自動設定語言、國家限制和官方網站過濾"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "返回結果數量（1-10），建議 8-10 筆以獲得足夠資料"
                    },
                    "date_restrict": {
                        "type": "string",
                        "enum": ["d7", "d30", "w2", "m1", "m3", "m6", "y1", "y2", "y5"],
                        "description": "時間限制：d7（7天內）、d30（30天內）、w2（2週內）、m1/m3/m6（1/3/6個月內）、y1/y2/y5（1/2/5年內）"
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"],
                        "description": "限制檔案類型，如 pdf（常用於官方法規文件）"
                    },
                    "exact_terms": {
                        "type": "string",
                        "description": "必須包含的精確詞彙（結果中一定要有這個詞）"
                    },
                    "exclude_terms": {
                        "type": "string",
                        "description": "排除的詞彙，用空格分隔多個詞（如：草案 draft 徵求意見）"
                    },
                    "or_terms": {
                        "type": "string",
                        "description": "至少包含其中一個詞彙，用空格分隔（如：資安 cybersecurity 網路安全）"
                    },
                    "sort_by_date": {
                        "type": "boolean",
                        "description": "是否按日期排序（true=最新的在前，適合找最新法規修訂）"
                    },
                    "disable_duplicate_filter": {
                        "type": "boolean",
                        "description": "關閉重複過濾以顯示更多結果（true=關閉過濾）"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_tw_laws",
            "description": "搜尋台灣全國法規資料庫。專門用於搜尋台灣的法律、法規命令。支援的類別包括：個資保護、資安、金融、電信、醫療。若查詢與台灣法規相關，優先使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜尋關鍵字，例如：個人資料保護、資通安全、電子簽章"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回結果數量上限，預設 10"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_tw_law_content",
            "description": "取得台灣法規的完整條文內容。需要先知道法規代碼（pcode）。常用法規代碼：I0050021（個人資料保護法）、A0030297（資通安全管理法）、J0080037（電子簽章法）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pcode": {
                        "type": "string",
                        "description": "法規代碼，例如：I0050021"
                    }
                },
                "required": ["pcode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "抓取指定網頁的內容。用於取得搜尋結果中特定網頁的詳細內容。可提取純文字或保留 HTML 格式。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要抓取的網頁 URL"
                    },
                    "extract_text": {
                        "type": "boolean",
                        "description": "是否只提取文字內容（移除 HTML 標籤），預設 true"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_pdf_content",
            "description": "下載並解析 PDF 檔案內容。用於處理 PDF 格式的法規文件、指引、報告等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "PDF 檔案的 URL"
                    },
                    "max_pages": {
                        "type": "integer",
                        "description": "最多解析的頁數，預設 10"
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "最大字元數，預設 5000"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_jp_laws",
            "description": "搜尋日本法規。使用內建的日本法規資料庫（包含 e-Gov 法令檢索系統的常用法規）。支援日文或中文關鍵字。涵蓋領域：資安（サイバーセキュリティ）、個資（個人情報）、金融、電信。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜尋關鍵字，可使用日文或中文"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["all", "法律", "政令", "府令", "規則", "ガイドライン"],
                        "description": "法規類別過濾"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_eu_laws",
            "description": "搜尋歐盟法規。使用內建的歐盟法規資料庫（包含 EUR-Lex 的常用法規）。涵蓋：GDPR、NIS 2 Directive、Cybersecurity Act、AI Act、DSA、DMA、DORA 等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜尋關鍵字，可使用英文或中文"
                    },
                    "doc_type": {
                        "type": "string",
                        "enum": ["all", "regulation", "directive", "decision"],
                        "description": "文件類型過濾：regulation（規則）、directive（指令）、decision（決定）"
                    }
                },
                "required": ["query"]
            }
        }
    },
]


def get_tool_schemas() -> list[dict]:
    """取得所有工具的 JSON Schema 定義"""
    return TOOL_SCHEMAS


def get_tool_names() -> list[str]:
    """取得所有工具名稱列表"""
    return [tool["function"]["name"] for tool in TOOL_SCHEMAS]


def get_tool_schema_by_name(name: str) -> dict | None:
    """根據名稱取得特定工具的 Schema"""
    for tool in TOOL_SCHEMAS:
        if tool["function"]["name"] == name:
            return tool
    return None
