#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬虫工厂

根据社区类型创建对应的爬虫实例
"""

from typing import Dict, Any
from loguru import logger
import os

from .reddit_crawler import RedditCrawler
from .reddit_playwright_crawler import RedditPlaywrightCrawler
from .github_crawler import GitHubCrawler
from .hackernews_crawler import HackerNewsCrawler
from .discourse_crawler import DiscourseCrawler
from .xiaohongshu_crawler import XiaohongshuCrawler
from .weibo_crawler import WeiboCrawler


class CrawlerFactory:
    """爬虫工厂类"""
    
    @staticmethod
    def create_crawler(source_type: str, url: str, config: Dict[str, Any] = None):
        """
        根据社区类型创建对应的爬虫
        
        Args:
            source_type: 社区类型 (reddit, github, hackernews, etc.)
            url: 社区URL
            config: 配置信息
            
        Returns:
            对应的爬虫实例
            
        Raises:
            ValueError: 不支持的社区类型
        """
        logger.debug(f"创建爬虫 - 类型: {source_type}, URL: {url}, 配置: {config}")
        config = config or {}
        
        try:
            if source_type == 'reddit':
                # 从URL提取subreddit名称
                # 支持格式: https://reddit.com/r/python 或 r/python
                subreddit_name = url.split('/r/')[-1].strip('/').split('/')[0]
                
                # 优先使用Playwright爬虫（无需API凭证）
                # 如果配置了API凭证，则使用API版本
                if os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
                    logger.info("使用 Reddit API 爬虫")
                    return RedditCrawler(subreddit_name, config)
                else:
                    logger.info("使用 Reddit Playwright 爬虫（无需API凭证）")
                    return RedditPlaywrightCrawler(subreddit_name, config)
            
            elif source_type == 'github':
                # 从URL提取仓库名称
                # 支持格式: https://github.com/owner/repo 或 owner/repo
                if 'github.com' in url:
                    parts = url.split('github.com/')[-1].strip('/').split('/')
                    repo_name = f"{parts[0]}/{parts[1]}"
                else:
                    repo_name = url.strip('/')
                return GitHubCrawler(repo_name, config)
            
            elif source_type == 'hackernews':
                # HackerNews不需要特定URL
                return HackerNewsCrawler(config)
            
            elif source_type == 'discourse':
                # Discourse 论坛（如 ethresear.ch）
                if not url:
                    raise ValueError("Discourse 爬虫需要提供 URL")
                
                # 提取基础URL
                if '://' in url:
                    forum_url = url.split('://')[0] + '://' + url.split('://')[1].split('/')[0]
                else:
                    forum_url = url
                return DiscourseCrawler(forum_url, config)
            
            elif source_type == 'xiaohongshu':
                # 小红书（需要 MindSpider）
                logger.info("使用小红书爬虫（需要 MindSpider 配置）")
                return XiaohongshuCrawler(config)
            
            elif source_type == 'weibo':
                # 微博（需要 MindSpider）
                logger.info("使用微博爬虫（需要 MindSpider 配置）")
                return WeiboCrawler(config)
            
            else:
                raise ValueError(f"不支持的社区类型: {source_type}")
        
        except Exception as e:
            logger.error(f"创建爬虫失败 ({source_type}): {e}")
            raise


if __name__ == "__main__":
    # 测试代码
    print("测试爬虫工厂...\n")
    
    # 测试 Reddit
    print("1. 测试 Reddit 爬虫:")
    reddit_crawler = CrawlerFactory.create_crawler(
        'reddit',
        'https://reddit.com/r/python',
        {'keywords': ['bug', 'issue']}
    )
    print(f"   创建成功: {reddit_crawler.__class__.__name__}\n")
    
    # 测试 GitHub
    print("2. 测试 GitHub 爬虫:")
    github_crawler = CrawlerFactory.create_crawler(
        'github',
        'https://github.com/fastapi/fastapi',
        {'keywords': ['bug', 'feature']}
    )
    print(f"   创建成功: {github_crawler.__class__.__name__}\n")
    
    # 测试 HackerNews
    print("3. 测试 HackerNews 爬虫:")
    hn_crawler = CrawlerFactory.create_crawler(
        'hackernews',
        'https://news.ycombinator.com',
        {}
    )
    print(f"   创建成功: {hn_crawler.__class__.__name__}\n")
    
    print("✅ 所有爬虫创建成功！")
