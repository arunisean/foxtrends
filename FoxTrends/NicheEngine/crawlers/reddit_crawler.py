#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reddit 爬虫

使用 PRAW (Python Reddit API Wrapper) 采集 Reddit 数据
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import praw
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class RedditCrawler:
    """
    Reddit 社区爬虫
    
    使用 PRAW 库采集 subreddit 的帖子数据
    """
    
    def __init__(self, subreddit_name: str, config: Dict[str, Any] = None):
        """
        初始化 Reddit 爬虫
        
        Args:
            subreddit_name: subreddit 名称（如 'python'）
            config: 配置信息
        """
        self.subreddit_name = subreddit_name.strip('/')
        self.config = config or {}
        self.keywords = self.config.get('keywords', [])
        
        # 初始化 Reddit 客户端
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID', ''),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET', ''),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'FoxTrends/1.0')
            )
            self.subreddit = self.reddit.subreddit(self.subreddit_name)
            logger.info(f"Reddit 爬虫初始化成功: r/{self.subreddit_name}")
        except Exception as e:
            logger.error(f"Reddit 爬虫初始化失败: {e}")
            raise
    
    def fetch_posts(self, limit: int = 50, sort: str = 'hot') -> List[Dict[str, Any]]:
        """
        获取帖子列表
        
        Args:
            limit: 获取数量限制
            sort: 排序方式 ('hot', 'new', 'top', 'rising')
            
        Returns:
            帖子列表
        """
        posts = []
        
        try:
            # 根据排序方式获取帖子
            if sort == 'hot':
                submissions = self.subreddit.hot(limit=limit)
            elif sort == 'new':
                submissions = self.subreddit.new(limit=limit)
            elif sort == 'top':
                submissions = self.subreddit.top(limit=limit, time_filter='week')
            elif sort == 'rising':
                submissions = self.subreddit.rising(limit=limit)
            else:
                submissions = self.subreddit.hot(limit=limit)
            
            for submission in submissions:
                try:
                    post = {
                        'id': submission.id,
                        'title': submission.title,
                        'content': submission.selftext or '',
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'url': f"https://reddit.com{submission.permalink}",
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'comments_count': submission.num_comments,
                        'created_at': datetime.fromtimestamp(submission.created_utc),
                        'is_self': submission.is_self,
                        'link_url': submission.url if not submission.is_self else None,
                    }
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"解析帖子失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(posts)} 条 Reddit 帖子")
            return posts
            
        except Exception as e:
            logger.error(f"获取 Reddit 帖子失败: {e}")
            return []
    
    def filter_by_keywords(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据关键词过滤帖子
        
        Args:
            posts: 帖子列表
            
        Returns:
            过滤后的帖子列表
        """
        if not self.keywords:
            return posts
        
        filtered = []
        for post in posts:
            title = post.get('title', '').lower()
            content = post.get('content', '').lower()
            
            # 检查是否包含任何关键词
            for keyword in self.keywords:
                keyword_lower = keyword.lower().strip()
                if keyword_lower in title or keyword_lower in content:
                    filtered.append(post)
                    break
        
        logger.info(f"关键词过滤: {len(posts)} -> {len(filtered)} 条帖子")
        return filtered
    
    def crawl(self, limit: int = 50, sort: str = 'hot') -> List[Dict[str, Any]]:
        """
        执行爬取任务
        
        Args:
            limit: 获取数量限制
            sort: 排序方式
            
        Returns:
            爬取到的帖子列表
        """
        # 获取帖子
        posts = self.fetch_posts(limit, sort)
        
        # 根据关键词过滤
        if self.keywords:
            posts = self.filter_by_keywords(posts)
        
        return posts


if __name__ == "__main__":
    # 测试代码
    crawler = RedditCrawler('python')
    posts = crawler.crawl(limit=10)
    
    print(f"\n获取到 {len(posts)} 条帖子:\n")
    for i, post in enumerate(posts[:5], 1):
        print(f"{i}. {post['title']}")
        print(f"   作者: {post['author']} | 评分: {post['score']} | 评论: {post['comments_count']}")
        print(f"   链接: {post['url']}\n")
