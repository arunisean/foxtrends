#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小红书爬虫适配器

集成 MindSpider 的小红书爬虫到 FoxTrends
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 检查 MindSpider 是否可用
MINDSPIDER_AVAILABLE = False
MindSpiderXHSCrawler = None

# 注意：由于 MindSpider 的配置复杂性，当前版本使用模拟模式
# 要启用真实爬虫，需要：
# 1. 完整安装 MindSpider 及其依赖
# 2. 配置 MindSpider 的 config 文件
# 3. 完成平台登录
logger.info("小红书爬虫当前使用模拟模式")


class XiaohongshuCrawler:
    """
    小红书爬虫适配器
    
    集成 MindSpider 的小红书爬虫功能
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化小红书爬虫
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
        self.keywords = self.config.get('keywords', [])
        
        if not MINDSPIDER_AVAILABLE:
            logger.warning("⚠️ MindSpider 未安装，小红书爬虫将使用模拟模式")
            logger.warning("请参考文档安装 MindSpider: https://github.com/666ghj/BettaFish")
            self.crawler = None
        else:
            try:
                # 初始化 MindSpider 爬虫
                self.crawler = self._init_mindspider_crawler()
                logger.info("小红书爬虫初始化成功")
            except Exception as e:
                logger.error(f"小红书爬虫初始化失败: {e}")
                self.crawler = None
    
    def _init_mindspider_crawler(self):
        """初始化 MindSpider 爬虫实例"""
        if not MINDSPIDER_AVAILABLE:
            return None
        
        try:
            # 这里需要根据 MindSpider 的实际API进行调整
            # 目前返回 None，表示需要进一步配置
            logger.info("正在初始化 MindSpider 小红书爬虫...")
            # crawler = MindSpiderXHSCrawler()
            # return crawler
            return None
        except Exception as e:
            logger.error(f"初始化 MindSpider 爬虫失败: {e}")
            return None
    
    async def fetch_posts_async(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        异步获取帖子列表
        
        Args:
            limit: 获取数量限制
            
        Returns:
            帖子列表
        """
        if not MINDSPIDER_AVAILABLE or self.crawler is None:
            return self._get_mock_data(limit)
        
        try:
            # 使用 MindSpider 爬虫采集数据
            # 这里需要根据 MindSpider 的实际API进行调整
            posts = []
            
            # 示例代码（需要根据实际API调整）:
            # for keyword in self.keywords[:3]:  # 限制关键词数量
            #     results = await self.crawler.search_notes(keyword, limit=limit//len(self.keywords))
            #     posts.extend(self._convert_to_standard_format(results))
            
            logger.info(f"成功获取 {len(posts)} 条小红书笔记")
            return posts[:limit]
            
        except Exception as e:
            logger.error(f"获取小红书笔记失败: {e}")
            return self._get_mock_data(limit)
    
    def _convert_to_standard_format(self, mindspider_posts: List[Any]) -> List[Dict[str, Any]]:
        """
        将 MindSpider 的数据格式转换为标准格式
        
        Args:
            mindspider_posts: MindSpider 返回的帖子列表
            
        Returns:
            标准格式的帖子列表
        """
        posts = []
        
        for post in mindspider_posts:
            try:
                # 根据 MindSpider 的数据结构进行转换
                standard_post = {
                    'id': str(post.get('note_id', '')),
                    'title': post.get('title', ''),
                    'content': post.get('desc', ''),
                    'author': post.get('nickname', 'unknown'),
                    'url': f"https://www.xiaohongshu.com/explore/{post.get('note_id', '')}",
                    'score': post.get('liked_count', 0),
                    'comments_count': post.get('comment_count', 0),
                    'created_at': datetime.fromtimestamp(post.get('time', 0)) if post.get('time') else datetime.now(),
                    'platform': 'xiaohongshu',
                    'tags': post.get('tag_list', []),
                }
                posts.append(standard_post)
            except Exception as e:
                logger.warning(f"转换帖子格式失败: {e}")
                continue
        
        return posts
    
    def _get_mock_data(self, limit: int) -> List[Dict[str, Any]]:
        """
        获取模拟数据（当 MindSpider 不可用时）
        
        Args:
            limit: 数量限制
            
        Returns:
            模拟数据列表
        """
        logger.info("⚠️ 使用模拟数据（MindSpider 未配置）")
        
        mock_posts = [
            {
                'id': f'mock_xhs_{i}',
                'title': f'小红书测试笔记 {i}',
                'content': '这是一条模拟的小红书笔记内容。请安装并配置 MindSpider 以获取真实数据。',
                'author': f'测试用户{i}',
                'url': f'https://www.xiaohongshu.com/explore/mock_{i}',
                'score': 100 + i * 10,
                'comments_count': 10 + i,
                'created_at': datetime.now(),
                'platform': 'xiaohongshu',
                'tags': ['测试', '模拟数据'],
                'note': '⚠️ 这是模拟数据，请配置 MindSpider 获取真实数据'
            }
            for i in range(min(limit, 5))
        ]
        
        return mock_posts
    
    def crawl(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        同步爬取方法（包装异步方法）
        
        Args:
            limit: 获取数量限制
            
        Returns:
            帖子列表
        """
        import asyncio
        return asyncio.run(self.fetch_posts_async(limit))


if __name__ == "__main__":
    # 测试代码
    print("测试小红书爬虫适配器...\n")
    
    crawler = XiaohongshuCrawler({'keywords': ['美妆', '穿搭']})
    posts = crawler.crawl(limit=5)
    
    print(f"\n✅ 成功获取 {len(posts)} 条笔记:\n")
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post['title']}")
        print(f"   作者: {post['author']} | 点赞: {post['score']} | 评论: {post['comments_count']}")
        if 'note' in post:
            print(f"   ⚠️  {post['note']}")
        print()
