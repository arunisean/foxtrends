#!/usr/bin/env python3
"""测试Playwright爬虫"""
import asyncio
import sys
sys.path.insert(0, '.')

from NicheEngine.crawlers.reddit_playwright_crawler import RedditPlaywrightCrawler

async def test():
    crawler = RedditPlaywrightCrawler('python')
    try:
        print("开始测试Playwright爬虫...")
        posts = await crawler.fetch_posts_async(limit=5)
        print(f'\n✓ 成功抓取 {len(posts)} 条帖子\n')
        for i, post in enumerate(posts, 1):
            print(f'{i}. {post["title"][:60]}...')
            print(f'   作者: {post["author"]} | 评论: {post["comments_count"]} | 分数: {post["score"]}')
            print()
    except Exception as e:
        print(f'✗ 错误: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test())
