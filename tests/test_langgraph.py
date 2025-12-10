"""
測試 LangGraph Agent 團隊
"""

import os

import pytest
from dotenv import load_dotenv

load_dotenv()

def test_langgraph_query():
    """測試 LangGraph 法規查詢"""
    # 跳過 CI 環境（需要真實 API 金鑰）
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key or api_key.startswith("test-"):
        pytest.skip("CI 測試環境，跳過 LangGraph 整合測試")

    print("=" * 60)
    print("測試 LangGraph Multi-Agent 法規查詢")
    print("=" * 60)
    print()

    try:
        from src.agents.langgraph_team import RegulationAgentTeam

        # 創建 Agent 團隊
        def status_callback(msg):
            print(f"[狀態] {msg}")

        team = RegulationAgentTeam(status_callback=status_callback)
        print("✅ LangGraph Agent 團隊創建成功")
        print()

        # 測試查詢
        test_query = "請查詢台灣的個人資料保護法"
        print(f"📝 測試查詢: {test_query}")
        print()

        for status, result in team.process_query(test_query):
            print(f"[進度] {status}")
            if result:
                print(f"[結果] 狀態: {result.get('status', 'N/A')}")
                if result.get("regulations"):
                    print(f"[結果] 找到 {len(result['regulations'])} 筆法規")

        print()
        print("✅ 查詢流程完成！")
        return True

    except Exception as e:
        print(f"❌ 查詢失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 開始測試 LangGraph Agent 團隊...\n")
    result = test_langgraph_query()

    if result:
        print("\n✅ 測試成功！")
    else:
        print("\n❌ 測試失敗")
