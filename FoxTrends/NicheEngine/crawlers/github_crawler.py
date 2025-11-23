#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub 爬虫

使用 PyGithub 采集 GitHub Issues 和 Discussions 数据
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from github import Github, GithubException
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class GitHubCrawler:
    """
    GitHub 仓库爬虫
    
    使用 PyGithub 库采集仓库的 Issues 数据
    """
    
    def __init__(self, repo_name: str, config: Dict[str, Any] = None):
        """
        初始化 GitHub 爬虫
        
        Args:
            repo_name: 仓库名称（如 'owner/repo'）
            config: 配置信息
        """
        self.repo_name = repo_name.strip('/')
        self.config = config or {}
        self.keywords = self.config.get('keywords', [])
        
        # 初始化 GitHub 客户端
        try:
            # 优先使用 settings 中的配置，然后尝试环境变量
            token = getattr(settings, 'GITHUB_TOKEN', None) or os.getenv('GITHUB_TOKEN', '')
            if token:
                self.github = Github(token)
                logger.info(f"使用 GitHub Token 认证（速率限制：5000次/小时）")
            else:
                self.github = Github()  # 未认证模式，速率限制更严格
                logger.warning("未配置 GITHUB_TOKEN，使用未认证模式（速率限制：60次/小时）")
            
            self.repo = self.github.get_repo(self.repo_name)
            logger.info(f"GitHub 爬虫初始化成功: {self.repo_name}")
        except GithubException as e:
            logger.error(f"GitHub 爬虫初始化失败: {e}")
            raise
    
    def fetch_issues(self, limit: int = 50, state: str = 'open') -> List[Dict[str, Any]]:
        """
        获取 Issues 列表
        
        Args:
            limit: 获取数量限制
            state: 状态 ('open', 'closed', 'all')
            
        Returns:
            Issues 列表
        """
        issues = []
        
        try:
            # 获取 Issues（按创建时间倒序）
            repo_issues = self.repo.get_issues(
                state=state,
                sort='created',
                direction='desc'
            )
            
            count = 0
            for issue in repo_issues:
                if count >= limit:
                    break
                
                # 跳过 Pull Requests
                if issue.pull_request:
                    continue
                
                try:
                    post = {
                        'id': str(issue.number),
                        'title': issue.title,
                        'content': issue.body or '',
                        'author': issue.user.login if issue.user else '[deleted]',
                        'url': issue.html_url,
                        'score': issue.reactions['total_count'] if issue.reactions else 0,
                        'comments_count': issue.comments,
                        'created_at': issue.created_at,
                        'updated_at': issue.updated_at,
                        'state': issue.state,
                        'labels': [label.name for label in issue.labels],
                    }
                    issues.append(post)
                    count += 1
                except Exception as e:
                    logger.warning(f"解析 Issue 失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(issues)} 条 GitHub Issues")
            return issues
            
        except GithubException as e:
            logger.error(f"获取 GitHub Issues 失败: {e}")
            return []
    
    def filter_by_keywords(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据关键词过滤 Issues
        
        Args:
            posts: Issues 列表
            
        Returns:
            过滤后的 Issues 列表
        """
        if not self.keywords:
            return posts
        
        filtered = []
        for post in posts:
            title = post.get('title', '').lower()
            content = post.get('content', '').lower()
            labels = ' '.join(post.get('labels', [])).lower()
            
            # 检查是否包含任何关键词
            for keyword in self.keywords:
                keyword_lower = keyword.lower().strip()
                if keyword_lower in title or keyword_lower in content or keyword_lower in labels:
                    filtered.append(post)
                    break
        
        logger.info(f"关键词过滤: {len(posts)} -> {len(filtered)} 条 Issues")
        return filtered
    
    def crawl(self, limit: int = 50, state: str = 'open') -> List[Dict[str, Any]]:
        """
        执行爬取任务
        
        Args:
            limit: 获取数量限制
            state: Issue 状态
            
        Returns:
            爬取到的 Issues 列表
        """
        # 获取 Issues
        posts = self.fetch_issues(limit, state)
        
        # 根据关键词过滤
        if self.keywords:
            posts = self.filter_by_keywords(posts)
        
        return posts
    
    async def fetch_posts_async(self, limit: int = 50, state: str = 'open') -> List[Dict[str, Any]]:
        """
        异步获取帖子列表（包装同步方法）
        
        Args:
            limit: 获取数量限制
            state: Issue 状态
            
        Returns:
            Issues 列表
        """
        import asyncio
        # PyGithub 是同步库，在线程池中运行
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.crawl, limit, state)


if __name__ == "__main__":
    # 测试代码
    crawler = GitHubCrawler('fastapi/fastapi')
    posts = crawler.crawl(limit=10)
    
    print(f"\n获取到 {len(posts)} 条 Issues:\n")
    for i, post in enumerate(posts[:5], 1):
        print(f"{i}. {post['title']}")
        print(f"   作者: {post['author']} | 反应: {post['score']} | 评论: {post['comments_count']}")
        print(f"   状态: {post['state']} | 标签: {', '.join(post['labels'])}")
        print(f"   链接: {post['url']}\n")
