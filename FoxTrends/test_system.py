"""
FoxTrends 系统测试脚本
验证核心功能是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_config():
    """测试配置系统"""
    print("测试配置系统...")
    from config import settings
    assert settings.HOST is not None
    assert settings.PORT is not None
    print("✓ 配置系统正常")


def test_database():
    """测试数据库连接"""
    print("\n测试数据库...")
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    print("✓ 数据库管理器初始化成功")


def test_agents():
    """测试Agent系统"""
    print("\n测试Agent系统...")
    from CommunityInsightAgent.agent import CommunityInsightAgent
    from ContentAnalysisAgent.agent import ContentAnalysisAgent
    from TrendDiscoveryAgent.agent import TrendDiscoveryAgent
    
    # 测试CommunityInsightAgent
    agent1 = CommunityInsightAgent()
    result1 = agent1.run("测试查询")
    assert result1['success'] == True
    print("✓ CommunityInsightAgent 正常")
    
    # 测试ContentAnalysisAgent
    agent2 = ContentAnalysisAgent()
    result2 = agent2.run("测试查询")
    assert result2['success'] == True
    print("✓ ContentAnalysisAgent 正常")
    
    # 测试TrendDiscoveryAgent
    agent3 = TrendDiscoveryAgent()
    result3 = agent3.run("测试查询")
    assert result3['success'] == True
    print("✓ TrendDiscoveryAgent 正常")


def test_niche_engine():
    """测试NicheEngine"""
    print("\n测试NicheEngine...")
    from NicheEngine.engine import NicheEngine
    from NicheEngine.models import DemandSignal
    
    engine = NicheEngine()
    
    # 测试添加社区
    community = engine.add_community(
        name="测试社区",
        source_type="reddit",
        config={"subreddit": "test"}
    )
    assert community.id is not None
    print("✓ 添加社区功能正常")
    
    # 测试需求信号提取
    signals = engine.extract_demand_signals("I need a better error message")
    assert isinstance(signals, list)
    print("✓ 需求信号提取功能正常")
    
    # 测试热度计算
    if signals:
        hotness = engine.calculate_hotness(
            signal=signals[0],
            discussion_count=10,
            participant_count=5
        )
        assert 0 <= hotness <= 100
        print(f"✓ 热度计算功能正常 (热度: {hotness:.1f})")
    
    # 测试监控状态
    success = engine.start_monitoring(community.id)
    assert success == True
    print("✓ 监控状态管理正常")


def test_forum_engine():
    """测试ForumEngine"""
    print("\n测试ForumEngine...")
    from ForumEngine.monitor import LogMonitor
    
    monitor = LogMonitor()
    assert monitor.log_dir is not None
    print("✓ ForumEngine 初始化正常")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("FoxTrends 系统测试")
    print("=" * 50)
    
    results = []
    
    results.append(("配置系统", test_config()))
    results.append(("数据库", test_database()))
    results.append(("Agent系统", test_agents()))
    results.append(("NicheEngine", test_niche_engine()))
    results.append(("ForumEngine", test_forum_engine()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以使用。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
