#!/usr/bin/env python3
"""
测试爬虫功能

验证Reddit、GitHub、HackerNews爬虫是否正常工作
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from NicheEngine.crawlers.factory import CrawlerFactory
from loguru import logger

def test_reddit():
    """测试Reddit爬虫"""
    print("\n" + "="*60)
    print("测试 Reddit 爬虫")
    print("="*60)
    
    try:
        crawler = CrawlerFactory.create_crawler(
            'reddit',
            'https://reddit.com/r/python',
            {'keywords': []}
        )
        
        posts = crawler.crawl(limit=5)
        
        print(f"\n✅ 成功获取 {len(posts)} 条帖子:\n")
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post['title'][:80]}")
            print(f"   作者: {post['author']} | 评分: {post['score']} | 评论: {post['comments_count']}")
            print(f"   链接: {post['url']}\n")
        
        return True
    except Exception as e:
        print(f"\n❌ Reddit 爬虫测试失败: {e}\n")
        logger.exception("Reddit爬虫测试失败")
        return False


def test_github():
    """测试GitHub爬虫"""
    print("\n" + "="*60)
    print("测试 GitHub 爬虫")
    print("="*60)
    
    try:
        crawler = CrawlerFactory.create_crawler(
            'github',
            'https://github.com/fastapi/fastapi',
            {'keywords': []}
        )
        
        posts = crawler.crawl(limit=5)
        
        print(f"\n✅ 成功获取 {len(posts)} 条 Issues:\n")
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post['title'][:80]}")
            print(f"   作者: {post['author']} | 反应: {post['score']} | 评论: {post['comments_count']}")
            print(f"   状态: {post['state']} | 标签: {', '.join(post['labels'][:3])}")
            print(f"   链接: {post['url']}\n")
        
        return True
    except Exception as e:
        print(f"\n❌ GitHub 爬虫测试失败: {e}\n")
        logger.exception("GitHub爬虫测试失败")
        return False


def test_hackernews():
    """测试HackerNews爬虫"""
    print("\n" + "="*60)
    print("测试 HackerNews 爬虫")
    print("="*60)
    
    try:
        crawler = CrawlerFactory.create_crawler(
            'hackernews',
            'https://news.ycombinator.com',
            {'keywords': []}
        )
        
        posts = crawler.crawl(limit=5)
        
        print(f"\n✅ 成功获取 {len(posts)} 条故事:\n")
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post['title'][:80]}")
            print(f"   作者: {post['author']} | 评分: {post['score']} | 评论: {post['comments_count']}")
            print(f"   链接: {post['url']}\n")
        
        return True
    except Exception as e:
        print(f"\n❌ HackerNews 爬虫测试失败: {e}\n")
        logger.exception("HackerNews爬虫测试失败")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("FoxTrends 爬虫功能测试")
    print("="*60)
    
    results = {
        'Reddit': test_reddit(),
        'GitHub': test_github(),
        'HackerNews': test_hackernews(),
    }
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for platform, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{platform:15} {status}")
    
    print("\n" + "="*60)
    
    all_passed = all(results.values())
    if all_passed:
        print("🎉 所有爬虫测试通过！")
    else:
        print("⚠️  部分爬虫测试失败，请检查配置")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
