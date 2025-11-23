#!/usr/bin/env python3
"""测试完整的监控流程"""
import asyncio
import sys
sys.path.insert(0, '.')

from database.db_manager import DatabaseManager
from NicheEngine.models import Community, DemandSignal
from NicheEngine.crawlers.factory import CrawlerFactory

async def test_full_monitoring():
    """测试完整的监控流程"""
    db = DatabaseManager()
    
    # 1. 添加测试社区
    print("=" * 60)
    print("步骤 1: 添加测试社区")
    print("=" * 60)
    
    test_communities = [
        {
            'name': 'Python Reddit',
            'source_url': 'https://www.reddit.com/r/python/',
            'source_type': 'reddit',
            'config': {
                'description': 'Python编程社区',
                'keywords': ['async', 'django', 'flask']
            }
        },
        {
            'name': 'FastAPI GitHub',
            'source_url': 'https://github.com/tiangolo/fastapi',
            'source_type': 'github',
            'config': {
                'description': 'FastAPI框架',
                'keywords': ['bug', 'feature', 'performance']
            }
        }
    ]
    
    added_communities = []
    for comm_data in test_communities:
        community = Community(**comm_data)
        success = db.add_community(community)
        if success:
            print(f"✓ 添加社区: {community.name}")
            # 重新获取以获得ID
            community = db.get_community_by_url(community.source_url)
            added_communities.append(community)
        else:
            print(f"✗ 添加失败: {community.name}")
    
    # 2. 运行爬虫采集数据
    print("\n" + "=" * 60)
    print("步骤 2: 运行爬虫采集数据")
    print("=" * 60)
    
    for community in added_communities:
        print(f"\n正在采集: {community.name}")
        
        try:
            # 创建爬虫
            crawler = CrawlerFactory.create_crawler(
                community.source_type,
                community.source_url,
                community.config
            )
            
            # 采集数据
            posts = await crawler.fetch_posts_async(limit=5)
            print(f"  采集到 {len(posts)} 条帖子")
            
            # 转换为需求信号并保存
            for post in posts:
                signal = DemandSignal(
                    community_id=community.id,
                    signal_type='discussion',
                    title=post.get('title', ''),
                    content=post.get('content', ''),
                    source_url=post.get('url', ''),
                    author=post.get('author', ''),
                    sentiment_score=0.0,
                    hotness_score=float(post.get('score', 0)),
                    metadata={
                        'comments_count': post.get('comments_count', 0),
                        'score': post.get('score', 0)
                    }
                )
                db.add_signal(signal)
            
            print(f"  ✓ 保存了 {len(posts)} 条需求信号")
            
        except Exception as e:
            print(f"  ✗ 采集失败: {e}")
    
    # 3. 查看结果
    print("\n" + "=" * 60)
    print("步骤 3: 查看监控结果")
    print("=" * 60)
    
    for community in added_communities:
        print(f"\n社区: {community.name}")
        print(f"  平台: {community.source_type}")
        print(f"  URL: {community.source_url}")
        
        # 获取需求信号
        signals = db.get_signals_by_community(community.id, limit=5)
        print(f"  需求信号数: {len(signals)}")
        
        for i, signal in enumerate(signals, 1):
            print(f"\n  信号 {i}:")
            print(f"    标题: {signal.title[:60]}...")
            print(f"    热度: {signal.hotness_score:.2f}")
            print(f"    作者: {signal.author}")
    
    # 4. 清理测试数据
    print("\n" + "=" * 60)
    print("步骤 4: 清理测试数据")
    print("=" * 60)
    
    for community in added_communities:
        # 删除需求信号
        signals = db.get_signals_by_community(community.id)
        for signal in signals:
            db.delete_signal(signal.id)
        
        # 删除社区
        db.delete_community(community.id)
        print(f"✓ 清理社区: {community.name}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_full_monitoring())
