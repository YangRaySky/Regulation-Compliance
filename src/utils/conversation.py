"""
對話歷史管理器

管理 LangGraph Agent 的多輪對話歷史。
使用滑動窗口機制保留最近 N 輪對話（預設 10 輪 = 20 條訊息）。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ConversationTurn:
    """單一對話輪次"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)


class ConversationHistory:
    """管理單一 Session 的對話歷史"""

    def __init__(self, max_turns: int = 10):
        """
        初始化對話歷史

        Args:
            max_turns: 最大保留輪數（1 輪 = 1 user + 1 assistant 訊息）
        """
        self.max_turns = max_turns
        self._history: list[ConversationTurn] = []

    def add_user_message(self, content: str, metadata: dict = None) -> None:
        """新增用戶訊息"""
        self._history.append(ConversationTurn(
            role="user",
            content=content,
            metadata=metadata or {}
        ))
        self._trim()

    def add_assistant_message(self, content: str, metadata: dict = None) -> None:
        """新增助手回應"""
        self._history.append(ConversationTurn(
            role="assistant",
            content=content,
            metadata=metadata or {}
        ))
        self._trim()

    def _trim(self) -> None:
        """截斷歷史至最大輪數"""
        max_messages = self.max_turns * 2  # 10 輪 = 20 條訊息
        if len(self._history) > max_messages:
            self._history = self._history[-max_messages:]

    def get_history(self) -> list[ConversationTurn]:
        """取得所有對話歷史"""
        return self._history.copy()

    def get_formatted_history(self) -> str:
        """
        格式化歷史以供 LLM prompt 使用

        Returns:
            格式化的對話歷史字串
        """
        if not self._history:
            return ""

        formatted = []
        for turn in self._history:
            role_label = "使用者" if turn.role == "user" else "助手"
            # 截斷過長的助手回應以節省 token
            content = turn.content
            if len(content) > 500 and turn.role == "assistant":
                content = content[:500] + "...(回應已截斷)"
            formatted.append(f"[{role_label}]: {content}")

        return "\n\n".join(formatted)

    def get_last_assistant_result(self) -> Optional[dict]:
        """取得最後一次助手回應的 metadata（用於追問查詢）"""
        for turn in reversed(self._history):
            if turn.role == "assistant" and turn.metadata:
                return turn.metadata
        return None

    def clear(self) -> None:
        """清除所有歷史"""
        self._history = []

    def __len__(self) -> int:
        return len(self._history)


# ===== Session 管理 =====
_conversations: dict[str, ConversationHistory] = {}


def get_conversation(session_id: str, max_turns: int = 10) -> ConversationHistory:
    """
    取得或建立指定 Session 的對話歷史

    Args:
        session_id: Session 識別碼
        max_turns: 最大保留輪數

    Returns:
        ConversationHistory 實例
    """
    if session_id not in _conversations:
        _conversations[session_id] = ConversationHistory(max_turns=max_turns)
    return _conversations[session_id]


def clear_conversation(session_id: str) -> None:
    """清除指定 Session 的對話歷史"""
    if session_id in _conversations:
        _conversations[session_id].clear()


def reset_all_conversations() -> None:
    """重置所有對話歷史（用於測試）"""
    _conversations.clear()
