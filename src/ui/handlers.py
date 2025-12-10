"""
UI 事件處理器

處理使用者操作與 LangGraph Agent 系統的互動。
使用多 Agent 協作完成法規查詢任務。
"""

from typing import Optional, Generator

from ..utils.config import validate_config


class RegulationQueryHandler:
    """
    法規查詢處理器

    使用 LangGraph 多 Agent 團隊實現真正的 Agent 架構：
    - Planner: 分析查詢並規劃策略
    - Researcher: 執行搜尋（使用工具）
    - Validator: 驗證結果準確性
    """

    def __init__(self):
        """初始化處理器"""
        self.agents_initialized = False
        self.agent_team = None

    def initialize_agents(self) -> bool:
        """
        初始化 Agent 系統

        Returns:
            是否初始化成功
        """
        if not validate_config():
            return False

        try:
            from ..agents.langgraph_team import get_agent_team
            self.agent_team = get_agent_team()
            print("✓ LangGraph Agent 團隊初始化成功")

        except Exception as e:
            print(f"Agent 初始化失敗: {e}")
            return False

        self.agents_initialized = True
        return True

    def process_query(
        self,
        query: str,
        jurisdiction: str = "自動偵測",
        regulation_type: Optional[str] = None,
        target_language: Optional[str] = None,
        skip_cache: bool = False,
        conversation_history: str = "",
        previous_results_summary: str = "",
    ) -> Generator[tuple[str, Optional[dict]], None, None]:
        """
        處理法規查詢

        Args:
            query: 使用者查詢
            jurisdiction: 目標地區
            regulation_type: 法規類型
            target_language: 翻譯目標語言
            skip_cache: 是否跳過快取（強制重新查詢）
            conversation_history: 格式化的對話歷史（多輪對話支援）
            previous_results_summary: 上次查詢結果摘要（用於追問）

        Yields:
            (狀態訊息, 結果資料)
        """
        # 檢查 Agent 是否已初始化
        if not self.agents_initialized:
            yield ("正在初始化 Agent 系統...", None)
            if not self.initialize_agents():
                yield ("❌ Agent 初始化失敗，請檢查環境設定", None)
                return

        yield ("✅ Agent 系統已就緒 (LangGraph Multi-Agent)", None)
        yield (f"📝 收到查詢請求:\n{query}", None)

        # 使用 LangGraph 多 Agent 團隊處理查詢
        yield from self._process_with_langgraph(
            query,
            jurisdiction,
            skip_cache=skip_cache,
            conversation_history=conversation_history,
            previous_results_summary=previous_results_summary,
        )

    def _process_with_langgraph(
        self,
        query: str,
        jurisdiction: str,
        skip_cache: bool = False,
        conversation_history: str = "",
        previous_results_summary: str = "",
    ) -> Generator[tuple[str, Optional[dict]], None, None]:
        """使用 LangGraph 多 Agent 處理查詢"""
        try:
            for status, result in self.agent_team.process_query(
                query,
                jurisdiction,
                skip_cache=skip_cache,
                conversation_history=conversation_history,
                previous_results_summary=previous_results_summary,
            ):
                yield (status, result)

                if result:
                    # 補充 query 資訊
                    result["query"] = query
                    result["jurisdiction"] = jurisdiction

        except Exception as e:
            yield (f"❌ 處理失敗: {str(e)}", {
                "status": "error",
                "error": str(e),
            })


# 全域處理器實例
_handler: Optional[RegulationQueryHandler] = None


def get_handler() -> RegulationQueryHandler:
    """取得全域處理器實例"""
    global _handler
    if _handler is None:
        _handler = RegulationQueryHandler()
    return _handler


def reset_handler():
    """重置處理器"""
    global _handler
    _handler = None
