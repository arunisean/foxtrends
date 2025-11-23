#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HackerNews 爬虫

使用 HackerNews 官方 API 采集数据
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import requests
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class HackerNewsCrawler:
    """
    HackerNews 爬虫
    
    使用官方 Firebase API 采集热门故事
    """
    
    API_BASE = "https://hacker-news.firebaseio.com/v0"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化 HackerNews 爬虫
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
        self.keywords = self.config.get('keywords', [])
        logger.info("HackerNews 爬虫初始化成功")
    
    def _get_item(self, item_id: int) -> Dict[str, Any]:
        """
        获取单个item的详细信息
        
        Args:
            item_id: Item ID
            
        Returns:
            Item详细信息
        """
        try:
            response = requests.get(f"{self.API_BASE}/item/{item_id}.json", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"获取item {item_id} 失败: {e}")
            return {}
    
    def fetch_stories(self, limit: int = 50, story_type: str = 'top') -> List[Dict[str, Any]]:
        """
        获取故事列表
        
        Args:
            limit: 获取数量限制
            story_type: 故事类型 ('top', 'new', 'best')
            
        Returns:
            故事列表
        """
        stories = []
        
        try:
            # 获取故事ID列表
            if story_type == 'top':
                endpoint = f"{self.API_BASE}/topstories.json"
            elif story_type == 'new':
                endpoint = f"{self.API_BASE}/newstories.json"
            elif story_type == 'best':
                endpoint = f"{self.API_BASE}/beststories.json"
            else:
                endpoint = f"{self.API_BASE}/topstories.json"
            
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:limit]
            
            # 获取每个故事的详细信息
            for story_id in story_ids:
                item = self._get_item(story_id)
                
                if not item or item.get('type') != 'story':
                    continue
                
                try:
                    post = {
                        'id': str(item.get('id', '')),
                        'title': item.get('title', ''),
                        'content': item.get('text', ''),
                        'author': item.get('by', '[deleted]'),
                        'url': item.get('url', f"https://news.ycombinator.com/item?id={item.get('id', '')}"),
                        'score': item.get('score', 0),
                        'comments_count': item.get('descendants', 0),
                        'created_at': datetime.fromtimestamp(item.get('time', 0)) if item.get('time') else datetime.now(),
                    }
                    stories.append(post)
                except Exception as e:
                    logger.warning(f"解析故事失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(stories)} 条 HackerNews 故事")
            return stories
            
        except Exception as e:
            logger.error(f"获取 HackerNews 故事失败: {e}")
            return []
    
    def filter_by_keywords(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据关键词过滤故事
        
        Args:
            posts: 故事列表
            
        Returns:
            过滤后的故事列表
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
        
        logger.info(f"关键词过滤: {len(posts)} -> {len(filtered)} 条故事")
        return filtered
    
    def crawl(self, limit: int = 50, story_type: str = 'top') -> List[Dict[str, Any]]:
        """
        执行爬取任务
        
        Args:
            limit: 获取数量限制
            story_type: 故事类型
            
        Returns:
            爬取到的故事列表
        """
        # 获取故事
        posts = self.fetch_stories(limit, story_type)
        
        # 根据关键词过滤
        if self.keywords:
            posts = self.filter_by_keywords(posts)
        
        return posts
    
    async def fetch_posts_async(self, limit: int = 50, story_type: str = 'top') -> List[Dict[str, Any]]:
        """
        异步获取帖子列表（包装同步方法）
        
        Args:
            limit: 获取数量限制
            story_type: 故事类型
            
        Returns:
            故事列表
        """
        import asyncio
        # hackernews 是同步库，在线程池中运行
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.crawl, limit, story_type)


if __name__ == "__main__":
    # 测试代码
    print("测试 HackerNews 爬虫...\n")
    
    crawler = HackerNewsCrawler()
    posts = crawler.crawl(limit=10)
    
    print(f"\n✅ 成功获取 {len(posts)} 条 HackerNews 故事:\n")
    for i, post in enumerate(posts[:5], 1):
        print(f"{i}. {post['title'][:80]}")
        print(f"   作者: {post['author']} | 评分: {post['score']} | 评论: {post['comments_count']}")
        print(f"   链接: {post['url']}\n")
