#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Discourse 论坛爬虫

支持所有基于 Discourse 的论坛，如 ethresear.ch, discuss.python.org 等
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import requests
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class DiscourseCrawler:
    """
    Discourse 论坛爬虫
    
    使用 Discourse API 采集论坛帖子和讨论
    """
    
    def __init__(self, forum_url: str, config: Dict[str, Any] = None):
        """
        初始化 Discourse 爬虫
        
        Args:
            forum_url: 论坛URL（如 'https://ethresear.ch'）
            config: 配置信息
        """
        self.forum_url = forum_url.rstrip('/')
        self.config = config or {}
        self.keywords = self.config.get('keywords', [])
        self.api_base = f"{self.forum_url}"
        
        # API Key（可选，用于提高速率限制）
        self.api_key = self.config.get('api_key', '')
        self.api_username = self.config.get('api_username', '')
        
        logger.info(f"Discourse 爬虫初始化成功: {self.forum_url}")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        发起 API 请求
        
        Args:
            endpoint: API 端点
            params: 请求参数
            
        Returns:
            响应数据
        """
        url = f"{self.api_base}{endpoint}"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'FoxTrends/1.0'
        }
        
        # 如果有 API Key，添加到请求头
        if self.api_key and self.api_username:
            headers['Api-Key'] = self.api_key
            headers['Api-Username'] = self.api_username
        
        try:
            response = requests.get(url, headers=headers, params=params or {}, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API 请求失败: {e}")
            return {}
    
    def fetch_latest_topics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取最新话题列表
        
        Args:
            limit: 获取数量限制
            
        Returns:
            话题列表
        """
        topics = []
        
        try:
            # 获取最新话题
            data = self._make_request('/latest.json', {'per_page': limit})
            
            if not data or 'topic_list' not in data:
                logger.warning("未获取到话题列表")
                return []
            
            topic_list = data['topic_list'].get('topics', [])
            
            for topic in topic_list[:limit]:
                try:
                    post = {
                        'id': str(topic.get('id', '')),
                        'title': topic.get('title', ''),
                        'content': topic.get('excerpt', ''),  # 摘要
                        'author': topic.get('last_poster_username', 'unknown'),
                        'url': f"{self.forum_url}/t/{topic.get('slug', '')}/{topic.get('id', '')}",
                        'score': topic.get('like_count', 0),
                        'comments_count': topic.get('posts_count', 0) - 1,  # 减去主帖
                        'views_count': topic.get('views', 0),
                        'created_at': datetime.fromisoformat(topic.get('created_at', '').replace('Z', '+00:00')) if topic.get('created_at') else datetime.now(),
                        'category': topic.get('category_id', 0),
                        'tags': topic.get('tags', []),
                        'pinned': topic.get('pinned', False),
                    }
                    topics.append(post)
                except Exception as e:
                    logger.warning(f"解析话题失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(topics)} 条 Discourse 话题")
            return topics
            
        except Exception as e:
            logger.error(f"获取 Discourse 话题失败: {e}")
            return []
    
    def fetch_top_topics(self, period: str = 'weekly', limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取热门话题列表
        
        Args:
            period: 时间周期 ('daily', 'weekly', 'monthly', 'yearly', 'all')
            limit: 获取数量限制
            
        Returns:
            话题列表
        """
        topics = []
        
        try:
            # 获取热门话题
            data = self._make_request(f'/top/{period}.json', {'per_page': limit})
            
            if not data or 'topic_list' not in data:
                logger.warning("未获取到热门话题列表")
                return []
            
            topic_list = data['topic_list'].get('topics', [])
            
            for topic in topic_list[:limit]:
                try:
                    post = {
                        'id': str(topic.get('id', '')),
                        'title': topic.get('title', ''),
                        'content': topic.get('excerpt', ''),
                        'author': topic.get('last_poster_username', 'unknown'),
                        'url': f"{self.forum_url}/t/{topic.get('slug', '')}/{topic.get('id', '')}",
                        'score': topic.get('like_count', 0),
                        'comments_count': topic.get('posts_count', 0) - 1,
                        'views_count': topic.get('views', 0),
                        'created_at': datetime.fromisoformat(topic.get('created_at', '').replace('Z', '+00:00')) if topic.get('created_at') else datetime.now(),
                        'category': topic.get('category_id', 0),
                        'tags': topic.get('tags', []),
                        'pinned': topic.get('pinned', False),
                    }
                    topics.append(post)
                except Exception as e:
                    logger.warning(f"解析话题失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(topics)} 条热门 Discourse 话题")
            return topics
            
        except Exception as e:
            logger.error(f"获取热门 Discourse 话题失败: {e}")
            return []
    
    def filter_by_keywords(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据关键词过滤话题
        
        Args:
            posts: 话题列表
            
        Returns:
            过滤后的话题列表
        """
        if not self.keywords:
            return posts
        
        filtered = []
        for post in posts:
            title = post.get('title', '').lower()
            content = post.get('content', '').lower()
            tags = ' '.join(post.get('tags', [])).lower()
            
            # 检查是否包含任何关键词
            for keyword in self.keywords:
                keyword_lower = keyword.lower().strip()
                if keyword_lower in title or keyword_lower in content or keyword_lower in tags:
                    filtered.append(post)
                    break
        
        logger.info(f"关键词过滤: {len(posts)} -> {len(filtered)} 条话题")
        return filtered
    
    def crawl(self, limit: int = 50, topic_type: str = 'latest') -> List[Dict[str, Any]]:
        """
        执行爬取任务
        
        Args:
            limit: 获取数量限制
            topic_type: 话题类型 ('latest', 'top')
            
        Returns:
            爬取到的话题列表
        """
        # 获取话题
        if topic_type == 'top':
            posts = self.fetch_top_topics(limit=limit)
        else:
            posts = self.fetch_latest_topics(limit=limit)
        
        # 根据关键词过滤
        if self.keywords:
            posts = self.filter_by_keywords(posts)
        
        return posts
    
    async def fetch_posts_async(self, limit: int = 50, topic_type: str = 'latest') -> List[Dict[str, Any]]:
        """
        异步获取帖子列表（包装同步方法）
        
        Args:
            limit: 获取数量限制
            topic_type: 话题类型
            
        Returns:
            话题列表
        """
        import asyncio
        # requests 是同步库，在线程池中运行
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.crawl, limit, topic_type)


if __name__ == "__main__":
    # 测试代码
    print("测试 Discourse 爬虫...\n")
    
    # 测试 ethresear.ch
    crawler = DiscourseCrawler('https://ethresear.ch')
    posts = crawler.crawl(limit=10)
    
    print(f"\n✅ 成功获取 {len(posts)} 条话题:\n")
    for i, post in enumerate(posts[:5], 1):
        print(f"{i}. {post['title'][:80]}")
        print(f"   作者: {post['author']} | 点赞: {post['score']} | 评论: {post['comments_count']} | 浏览: {post['views_count']}")
        print(f"   标签: {', '.join(post['tags'])}")
        print(f"   链接: {post['url']}\n")
