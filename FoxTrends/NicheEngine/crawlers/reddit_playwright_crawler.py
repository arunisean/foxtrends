#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reddit Playwright 爬虫

使用 Playwright 浏览器自动化采集 Reddit 数据（无需API凭证）
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright, Page
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class RedditPlaywrightCrawler:
    """
    Reddit Playwright 爬虫
    
    使用浏览器自动化采集 subreddit 数据，无需 API 凭证
    """
    
    def __init__(self, subreddit_name: str, config: Dict[str, Any] = None):
        """
        初始化 Reddit Playwright 爬虫
        
        Args:
            subreddit_name: subreddit 名称（如 'python'）
            config: 配置信息
        """
        self.subreddit_name = subreddit_name.strip('/')
        self.config = config or {}
        self.keywords = self.config.get('keywords', [])
        self.url = f"https://old.reddit.com/r/{self.subreddit_name}"
        logger.info(f"Reddit Playwright 爬虫初始化成功: r/{self.subreddit_name}")
    
    async def _extract_posts_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """
        从页面提取帖子信息
        
        Args:
            page: Playwright页面对象
            
        Returns:
            帖子列表
        """
        posts = []
        
        try:
            # 等待帖子加载
            await page.wait_for_selector('.thing', timeout=10000)
            
            # 获取所有帖子元素
            post_elements = await page.query_selector_all('.thing')
            
            for element in post_elements:
                try:
                    # 提取帖子ID
                    post_id = await element.get_attribute('data-fullname')
                    if not post_id:
                        continue
                    
                    # 提取标题
                    title_elem = await element.query_selector('a.title')
                    title = await title_elem.inner_text() if title_elem else ''
                    
                    # 提取链接
                    url = await title_elem.get_attribute('href') if title_elem else ''
                    if url and not url.startswith('http'):
                        url = f"https://old.reddit.com{url}"
                    
                    # 提取作者
                    author_elem = await element.query_selector('a.author')
                    author = await author_elem.inner_text() if author_elem else '[deleted]'
                    
                    # 提取评分
                    score_elem = await element.query_selector('.score.unvoted')
                    score_text = await score_elem.get_attribute('title') if score_elem else '0'
                    try:
                        score = int(score_text)
                    except:
                        score = 0
                    
                    # 提取评论数
                    comments_elem = await element.query_selector('a.comments')
                    comments_text = await comments_elem.inner_text() if comments_elem else '0 comments'
                    try:
                        comments_count = int(comments_text.split()[0])
                    except:
                        comments_count = 0
                    
                    # 提取内容（如果是文本帖）
                    content = ''
                    
                    post = {
                        'id': post_id,
                        'title': title,
                        'content': content,
                        'author': author,
                        'url': url,
                        'score': score,
                        'comments_count': comments_count,
                        'created_at': datetime.now(),  # 无法从页面获取精确时间
                    }
                    posts.append(post)
                    
                except Exception as e:
                    logger.warning(f"解析帖子失败: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"提取帖子失败: {e}")
            return []
    
    async def fetch_posts_async(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        异步获取帖子列表
        
        Args:
            limit: 获取数量限制
            
        Returns:
            帖子列表
        """
        posts = []
        
        try:
            async with async_playwright() as p:
                # 启动浏览器（使用无头模式）
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # 访问 subreddit
                logger.info(f"正在访问: {self.url}")
                await page.goto(self.url, wait_until='domcontentloaded', timeout=30000)
                
                # 提取帖子
                posts = await self._extract_posts_from_page(page)
                
                # 关闭浏览器
                await browser.close()
                
                # 限制数量
                posts = posts[:limit]
                
                logger.info(f"成功获取 {len(posts)} 条 Reddit 帖子")
                return posts
                
        except Exception as e:
            logger.error(f"获取 Reddit 帖子失败: {e}")
            return []
    
    def fetch_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        同步获取帖子列表（包装异步方法）
        
        Args:
            limit: 获取数量限制
            
        Returns:
            帖子列表
        """
        return asyncio.run(self.fetch_posts_async(limit))
    
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
    
    def crawl(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        执行爬取任务
        
        Args:
            limit: 获取数量限制
            
        Returns:
            爬取到的帖子列表
        """
        # 获取帖子
        posts = self.fetch_posts(limit)
        
        # 根据关键词过滤
        if self.keywords:
            posts = self.filter_by_keywords(posts)
        
        return posts


if __name__ == "__main__":
    # 测试代码
    print("测试 Reddit Playwright 爬虫...\n")
    
    crawler = RedditPlaywrightCrawler('python')
    posts = crawler.crawl(limit=10)
    
    print(f"\n✅ 成功获取 {len(posts)} 条帖子:\n")
    for i, post in enumerate(posts[:5], 1):
        print(f"{i}. {post['title'][:80]}")
        print(f"   作者: {post['author']} | 评分: {post['score']} | 评论: {post['comments_count']}")
        print(f"   链接: {post['url']}\n")
