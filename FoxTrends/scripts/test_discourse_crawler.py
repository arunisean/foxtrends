#!/usr/bin/env python3
"""测试Discourse爬虫"""
import asyncio
import sys
sys.path.insert(0, '.')

from NicheEngine.crawlers.discourse_crawler import DiscourseCrawler

async def test_discourse():
    """测试Discourse爬虫"""
    print("=" * 60)
    print("测试 Discourse 爬虫")
    print("=" * 60)
    
    # 测试 ethresear.ch
    print("\n1. 测试 Ethereum Research (ethresear.ch)")
    print("-" * 60)
    crawler = DiscourseCrawler('https://ethresear.ch')
    posts = await crawler.fetch_posts_async(limit=5)
    
    print(f"\n✓ 成功采集 {len(posts)} 条帖子\n")
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post['title'][:70]}")
        print(f"   作者: {post['author']} | 点赞: {post['score']} | 评论: {post['comments_count']} | 浏览: {post['views_count']}")
        if post['tags']:
            print(f"   标签: {', '.join(post['tags'])}")
        print()
    
    # 测试 Rust Users Forum
    print("\n2. 测试 Rust Users Forum")
    print("-" * 60)
    crawler2 = DiscourseCrawler('https://users.rust-lang.org', {'keywords': ['async', 'performance']})
    posts2 = await crawler2.fetch_posts_async(limit=5)
    
    print(f"\n✓ 成功采集 {len(posts2)} 条帖子\n")
    for i, post in enumerate(posts2, 1):
        print(f"{i}. {post['title'][:70]}")
        print(f"   作者: {post['author']} | 点赞: {post['score']} | 评论: {post['comments_count']}")
        print()
    
    print("=" * 60)
    print("✅ Discourse 爬虫测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_discourse())
