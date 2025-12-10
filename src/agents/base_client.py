"""
LLM 客戶端基底類別

提供 GPTClient 和 ClaudeClient 的共用功能：
- analyze_query: 分析法規查詢的清晰度
- search_regulations: 搜尋法規資訊
- _parse_json_response: 解析 LLM 回傳的 JSON
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """統一的 LLM 回應結構"""
    content: str
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[dict] = None


class BaseLLMClient(ABC):
    """
    LLM 客戶端基底類別

    這是一個抽象類別，定義了所有 LLM 客戶端必須實作的介面，
    並提供共用的方法實作。

    子類別必須實作：
    - chat(): 發送聊天訊息的核心方法
    """

    @abstractmethod
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """
        發送聊天訊息（由子類別實作）

        Args:
            message: 使用者訊息
            system_prompt: 系統提示詞
            max_tokens: 最大 token 數

        Returns:
            LLMResponse 物件
        """
        pass

    def _parse_json_response(self, content: str) -> dict:
        """
        解析 LLM 回傳的 JSON 內容

        支援以下格式：
        - ```json ... ```
        - ``` ... ```
        - 純 JSON 字串

        Args:
            content: LLM 回傳的原始內容

        Returns:
            解析後的字典

        Raises:
            json.JSONDecodeError: 若無法解析 JSON
        """
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()

        return json.loads(json_str)

    def analyze_query(self, query: str, jurisdiction: str) -> dict:
        """
        分析法規查詢的清晰度

        Args:
            query: 使用者查詢
            jurisdiction: UI 選擇的地區

        Returns:
            分析結果字典，包含：
            - is_clear: 查詢是否足夠清晰
            - confidence: 信心度 (0.0-1.0)
            - missing_info: 缺少的資訊類型列表
            - clarification_questions: 需要釐清的問題列表
            - understood: 已理解的查詢內容
        """
        system_prompt = """你是一個法規查詢分析專家。分析使用者的查詢，\
判斷是否足夠清晰。

你必須以 JSON 格式回應，格式如下：
```json
{
  "is_clear": true/false,
  "confidence": 0.0-1.0,
  "missing_info": ["缺少的資訊類型"],
  "clarification_questions": [
    {
      "question": "問題內容",
      "options": ["選項1", "選項2", "選項3"]
    }
  ],
  "understood": {
    "jurisdiction": "理解的地區",
    "regulation_type": "理解的法規類型",
    "specific_topic": "理解的具體主題"
  }
}
```

判斷規則：
1. 如果使用者明確指定了地區、法規名稱或具體主題，則 is_clear = true
2. 如果查詢太籠統（如「資安法規」「個資法」沒有指定地區），則 is_clear = false
3. 注意：使用者在 UI 選擇的地區可能與查詢內容不符（如選台灣但問日本法規）

只回應 JSON，不要有其他文字。"""

        message = f"""分析以下法規查詢：

使用者查詢：{query}
UI 選擇的地區：{jurisdiction}

請分析此查詢是否足夠清晰，並以 JSON 格式回應。"""

        try:
            response = self.chat(message, system_prompt=system_prompt)
            return self._parse_json_response(response.content)

        except Exception as e:
            print(f"LLM 分析失敗: {e}")
            return {
                "is_clear": True,
                "confidence": 0.5,
                "missing_info": [],
                "clarification_questions": [],
                "understood": {
                    "jurisdiction": jurisdiction,
                    "regulation_type": "未知",
                    "specific_topic": query,
                }
            }

    def search_regulations(
        self,
        query: str,
        jurisdiction: str,
        regulation_type: Optional[str] = None,
    ) -> dict:
        """
        搜尋法規資訊

        Args:
            query: 查詢內容
            jurisdiction: 地區
            regulation_type: 法規類型（可選）

        Returns:
            搜尋結果字典，包含：
            - found: 是否找到結果
            - regulations: 法規列表
            - notes: 補充說明
        """
        system_prompt = """你是一個資安法規搜尋專家。根據使用者的查詢，\
提供相關法規資訊。

你必須以 JSON 格式回應，格式如下：
```json
{
  "found": true/false,
  "regulations": [
    {
      "name": "法規名稱",
      "jurisdiction": "地區",
      "type": "法律/法規/標準/指引",
      "summary": "簡要說明",
      "key_points": ["重點1", "重點2"],
      "official_source": "官方來源URL（如果知道）",
      "last_updated": "最後更新日期（如果知道）"
    }
  ],
  "notes": "補充說明"
}
```

注意：
1. 提供真實存在的法規資訊
2. 如果不確定，請誠實說明
3. 對於不同地區的法規要準確區分"""

        message = f"""請搜尋以下法規資訊：

查詢：{query}
地區：{jurisdiction}
法規類型：{regulation_type or "不限"}

請提供相關的法規資訊。"""

        try:
            response = self.chat(message, system_prompt=system_prompt)
            return self._parse_json_response(response.content)

        except Exception as e:
            print(f"LLM 搜尋失敗: {e}")
            return {
                "found": False,
                "regulations": [],
                "notes": f"搜尋過程發生錯誤: {str(e)}"
            }
