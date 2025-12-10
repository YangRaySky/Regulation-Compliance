"""
對話歷史管理器測試

測試 ConversationHistory 類別和 Session 管理功能。
"""

from src.utils.conversation import (
    ConversationHistory,
    ConversationTurn,
    clear_conversation,
    get_conversation,
    reset_all_conversations,
)


class TestConversationTurn:
    """測試 ConversationTurn 資料類別"""

    def test_create_turn_with_defaults(self):
        """測試建立對話輪次（使用預設值）"""
        turn = ConversationTurn(role="user", content="Hello")
        assert turn.role == "user"
        assert turn.content == "Hello"
        assert turn.timestamp is not None
        assert turn.metadata == {}

    def test_create_turn_with_metadata(self):
        """測試建立對話輪次（含 metadata）"""
        turn = ConversationTurn(
            role="assistant",
            content="Hi there!",
            metadata={"count": 5},
        )
        assert turn.role == "assistant"
        assert turn.metadata == {"count": 5}


class TestConversationHistory:
    """測試 ConversationHistory 類別"""

    def test_init(self):
        """測試初始化"""
        history = ConversationHistory(max_turns=10)
        assert history.max_turns == 10
        assert len(history) == 0

    def test_add_user_message(self):
        """測試新增使用者訊息"""
        history = ConversationHistory(max_turns=10)
        history.add_user_message("Hello")

        assert len(history) == 1
        assert history.get_history()[0].role == "user"
        assert history.get_history()[0].content == "Hello"

    def test_add_assistant_message(self):
        """測試新增助手訊息"""
        history = ConversationHistory(max_turns=10)
        history.add_assistant_message("Hi there!", {"key": "value"})

        assert len(history) == 1
        assert history.get_history()[0].role == "assistant"
        assert history.get_history()[0].metadata == {"key": "value"}

    def test_trim_history(self):
        """測試歷史截斷功能"""
        history = ConversationHistory(max_turns=2)  # 2 輪 = 4 條訊息

        # 新增 6 條訊息（3 輪）
        for i in range(3):
            history.add_user_message(f"User message {i}")
            history.add_assistant_message(f"Assistant message {i}")

        # 應該只保留最後 4 條訊息（2 輪）
        assert len(history) == 4
        assert history.get_history()[0].content == "User message 1"

    def test_get_formatted_history(self):
        """測試格式化歷史輸出"""
        history = ConversationHistory(max_turns=10)
        history.add_user_message("What is GDPR?")
        history.add_assistant_message("GDPR is the General Data Protection Regulation.")

        formatted = history.get_formatted_history()
        assert "[使用者]: What is GDPR?" in formatted
        assert "[助手]: GDPR is the General Data Protection Regulation." in formatted

    def test_formatted_history_truncation(self):
        """測試長回應截斷"""
        history = ConversationHistory(max_turns=10)
        long_message = "A" * 1000
        history.add_assistant_message(long_message)

        formatted = history.get_formatted_history()
        assert "...(回應已截斷)" in formatted
        # 確保截斷後長度合理
        assert len(formatted) < len(long_message)

    def test_get_formatted_history_empty(self):
        """測試空歷史的格式化輸出"""
        history = ConversationHistory(max_turns=10)
        formatted = history.get_formatted_history()
        assert formatted == ""

    def test_get_last_assistant_result(self):
        """測試取得最後助手結果"""
        history = ConversationHistory(max_turns=10)
        history.add_user_message("Query 1")
        history.add_assistant_message("Response 1", {"count": 5})
        history.add_user_message("Query 2")

        result = history.get_last_assistant_result()
        assert result == {"count": 5}

    def test_get_last_assistant_result_none(self):
        """測試無助手結果時返回 None"""
        history = ConversationHistory(max_turns=10)
        history.add_user_message("Query 1")

        result = history.get_last_assistant_result()
        assert result is None

    def test_clear(self):
        """測試清除歷史"""
        history = ConversationHistory(max_turns=10)
        history.add_user_message("Test")
        history.clear()

        assert len(history) == 0

    def test_get_history_returns_copy(self):
        """測試 get_history 返回複本而非原始列表"""
        history = ConversationHistory(max_turns=10)
        history.add_user_message("Test")

        history_copy = history.get_history()
        history_copy.clear()

        # 原始歷史應不受影響
        assert len(history) == 1


class TestSessionManagement:
    """測試 Session 管理功能"""

    def setup_method(self):
        """每個測試前重置所有對話"""
        reset_all_conversations()

    def test_get_conversation_creates_new(self):
        """測試 get_conversation 建立新歷史"""
        conv = get_conversation("test_session")
        assert len(conv) == 0
        assert conv.max_turns == 10

    def test_get_conversation_custom_max_turns(self):
        """測試自訂 max_turns"""
        conv = get_conversation("custom_session", max_turns=5)
        assert conv.max_turns == 5

    def test_get_conversation_returns_same(self):
        """測試相同 Session 返回相同歷史"""
        conv1 = get_conversation("session_a")
        conv1.add_user_message("Hello")

        conv2 = get_conversation("session_a")
        assert len(conv2) == 1
        assert conv2.get_history()[0].content == "Hello"

    def test_different_sessions_are_independent(self):
        """測試不同 Session 是獨立的"""
        conv_a = get_conversation("session_a")
        conv_b = get_conversation("session_b")

        conv_a.add_user_message("Message for A")

        assert len(conv_a) == 1
        assert len(conv_b) == 0

    def test_clear_conversation(self):
        """測試清除特定 Session"""
        conv = get_conversation("clear_test")
        conv.add_user_message("Test")

        clear_conversation("clear_test")

        # 應該清除歷史但保留 Session
        new_conv = get_conversation("clear_test")
        assert len(new_conv) == 0

    def test_clear_nonexistent_conversation(self):
        """測試清除不存在的 Session（應無錯誤）"""
        # 這不應拋出錯誤
        clear_conversation("nonexistent_session")

    def test_reset_all_conversations(self):
        """測試重置所有對話"""
        get_conversation("session_1").add_user_message("Test 1")
        get_conversation("session_2").add_user_message("Test 2")

        reset_all_conversations()

        # 新取得的應該是空的
        assert len(get_conversation("session_1")) == 0
        assert len(get_conversation("session_2")) == 0


class TestMultiTurnScenarios:
    """測試多輪對話場景"""

    def setup_method(self):
        """每個測試前重置"""
        reset_all_conversations()

    def test_typical_conversation_flow(self):
        """測試典型對話流程"""
        conv = get_conversation("typical_flow")

        # 第一輪
        conv.add_user_message("日本的資訊安全法規")
        conv.add_assistant_message("找到 4 筆法規：\n1. サイバーセキュリティ基本法...")

        # 第二輪（追問）
        conv.add_user_message("還有其他嗎？")
        conv.add_assistant_message("讓我搜尋更多...")

        assert len(conv) == 4

        # 驗證格式化歷史
        formatted = conv.get_formatted_history()
        assert "日本的資訊安全法規" in formatted
        assert "還有其他嗎？" in formatted

    def test_conversation_with_10_turns(self):
        """測試 10 輪對話（達到上限）"""
        conv = get_conversation("full_history", max_turns=10)

        for i in range(10):
            conv.add_user_message(f"Question {i}")
            conv.add_assistant_message(f"Answer {i}")

        # 應該有 20 條訊息（10 輪）
        assert len(conv) == 20

    def test_conversation_exceeds_limit(self):
        """測試超過上限時的截斷"""
        conv = get_conversation("over_limit", max_turns=3)  # 3 輪 = 6 條

        for i in range(5):  # 新增 5 輪 = 10 條
            conv.add_user_message(f"Question {i}")
            conv.add_assistant_message(f"Answer {i}")

        # 應該只保留最後 6 條（3 輪）
        assert len(conv) == 6
        # 最早的應該是 Question 2
        assert conv.get_history()[0].content == "Question 2"
