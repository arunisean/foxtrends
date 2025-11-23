#!/usr/bin/env python3
"""测试中文社区爬虫"""
import asyncio
import sys
sys.path.insert(0, '.')

from NicheEngine.crawlers.xiaohongshu_crawler import XiaohongshuCrawler
from NicheEngine.crawlers.weibo_crawler import WeiboCrawler

async def test_chinese_crawlers():
    """测试中文社区爬虫"""
    print("=" * 60)
    print("测试中文社区爬虫")
    print("=" * 60)
    
    # 测试小红书
    print("\n1. 测试小红书爬虫")
    print("-" * 60)
    xhs_crawler = XiaohongshuCrawler({'keywords': ['美妆', '穿搭', '旅游']})
    xhs_posts = await xhs_crawler.fetch_posts_async(limit=3)
    
    print(f"\n✓ 成功采集 {len(xhs_posts)} 条笔记\n")
    for i, post in enumerate(xhs_posts, 1):
        print(f"{i}. {post['title']}")
        print(f"   作者: {post['author']} | 点赞: {post['score']} | 评论: {post['comments_count']}")
        if 'note' in post:
            print(f"   ⚠️  {post['note']}")
        print()
    
    # 测试微博
    print("\n2. 测试微博爬虫")
    print("-" * 60)
    weibo_crawler = WeiboCrawler({'keywords': ['科技', '新闻', '热搜']})
    weibo_posts = await weibo_crawler.fetch_posts_async(limit=3)
    
    print(f"\n✓ 成功采集 {len(weibo_posts)} 条微博\n")
    for i, post in enumerate(weibo_posts, 1):
        print(f"{i}. {post['title']}")
        print(f"   作者: {post['author']} | 点赞: {post['score']} | 评论: {post['comments_count']} | 转发: {post.get('reposts_count', 0)}")
        if 'note' in post:
            print(f"   ⚠️  {post['note']}")
        print()
    
    print("=" * 60)
    print("说明")
    print("=" * 60)
    print("⚠️  当前使用模拟数据模式")
    print("📝 要获取真实数据，需要：")
    print("   1. 安装 MindSpider 依赖")
    print("   2. 配置 MindSpider 爬虫")
    print("   3. 完成平台登录")
    print("\n📚 参考文档: MindSpider/README.md")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_chinese_crawlers())
