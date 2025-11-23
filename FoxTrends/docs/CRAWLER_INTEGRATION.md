# 爬虫集成方案

## 概述

FoxTrends 使用成熟的开源爬虫库来采集各个社区的数据，而不是从头实现。这样可以：
- 快速集成，减少开发时间
- 利用社区维护的稳定代码
- 获得持续的更新和bug修复

## 推荐的开源爬虫库

### 1. Reddit - PRAW (Python Reddit API Wrapper)

**项目地址**: https://github.com/praw-dev/praw

**特点**:
- Reddit官方推荐的Python库
- 完整的API封装
- 支持OAuth认证
- 活跃维护，文档完善

**安装**:
```bash
uv add praw
```

**使用示例**:
```python
import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="FoxTrends/1.0"
)

# 获取subreddit的热门帖子
subreddit = reddit.subreddit("python")
for post in subreddit.hot(limit=50):
    print(post.title, post.score, post.num_comments)
```

**配置需求**:
- Reddit API credentials (免费申请)
- 在 https://www.reddit.com/prefs/apps 创建应用

### 2. GitHub - PyGithub

**项目地址**: https://github.com/PyGithub/PyGithub

**特点**:
- GitHub API v3 的完整封装
- 支持Issues、Discussions、Pull Requests
- 支持认证和速率限制处理

**安装**:
```bash
uv add PyGithub
```

**使用示例**:
```python
from github import Github

g = Github("YOUR_GITHUB_TOKEN")

# 获取仓库的Issues
repo = g.get_repo("fastapi/fastapi")
for issue in repo.get_issues(state='open', sort='created'):
    print(issue.title, issue.comments, issue.created_at)
```

**配置需求**:
- GitHub Personal Access Token (免费)
- 在 https://github.com/settings/tokens 创建

### 3. HackerNews - hackernews (非官方API)

**项目地址**: https://github.com/karan/HackerNewsAPI

**特点**:
- 简单易用的HackerNews API封装
- 支持获取热门、最新、最佳帖子
- 无需认证

**安装**:
```bash
uv add hackernews
```

**使用示例**:
```python
from hackernews import HackerNews

hn = HackerNews()

# 获取热门故事
for story_id in hn.top_stories(limit=50):
    story = hn.get_item(story_id)
    print(story.title, story.score, story.descendants)
```

### 4. 中文社交媒体 - MediaCrawler (已集成)

**项目地址**: https://github.com/NanmiCoder/MediaCrawler

**特点**:
- 支持小红书、抖音、快手、B站、微博等
- 使用Playwright进行浏览器自动化
- 已在BettaFish/MindSpider中使用

**位置**: `MindSpider/DeepSentimentCrawling/MediaCrawler/`

**使用示例**:
```python
# 已在 MindSpider 中实现
from MindSpider.DeepSentimentCrawling.platform_crawler import PlatformCrawler

crawler = PlatformCrawler(platform='xiaohongshu')
results = await crawler.crawl(keywords=['Python开发'])
```

### 5. Discourse论坛 - discourse-api

**项目地址**: https://github.com/bennylope/python-discourse

**特点**:
- 支持所有Discourse论坛（如Ethereum Research）
- RESTful API封装
- 支持帖子、评论、用户等

**安装**:
```bash
uv add python-discourse
```

**使用示例**:
```python
from discourse import Discourse

discourse = Discourse(
    'https://ethresear.ch',
    api_username='YOUR_USERNAME',
    api_key='YOUR_API_KEY'
)

# 获取最新帖子
topics = discourse.latest_topics()
for topic in topics['topic_list']['topics']:
    print(topic['title'], topic['posts_count'])
```

## 集成架构

### 目录结构

```
FoxTrends/NicheEngine/crawlers/
├── __init__.py
├── base_crawler.py          # 基础爬虫接口
├── reddit_crawler.py        # Reddit爬虫 (使用PRAW)
├── github_crawler.py        # GitHub爬虫 (使用PyGithub)
├── hackernews_crawler.py    # HackerNews爬虫
├── discourse_crawler.py     # Discourse论坛爬虫
└── chinese_social_crawler.py # 中文社交媒体爬虫 (集成MediaCrawler)
```

### 爬虫工厂模式

```python
# FoxTrends/NicheEngine/crawlers/factory.py
from typing import Dict, Any
from .base_crawler import BaseCrawler
from .reddit_crawler import RedditCrawler
from .github_crawler import GitHubCrawler
from .hackernews_crawler import HackerNewsCrawler
from .discourse_crawler import DiscourseCrawler
from .chinese_social_crawler import ChineseSocialCrawler

class CrawlerFactory:
    """爬虫工厂"""
    
    @staticmethod
    def create_crawler(source_type: str, url: str, config: Dict[str, Any]) -> BaseCrawler:
        """
        根据社区类型创建对应的爬虫
        
        Args:
            source_type: 社区类型 (reddit, github, hackernews, discourse, xiaohongshu, etc.)
            url: 社区URL
            config: 配置信息
            
        Returns:
            对应的爬虫实例
        """
        crawlers = {
            'reddit': RedditCrawler,
            'github': GitHubCrawler,
            'hackernews': HackerNewsCrawler,
            'discourse': DiscourseCrawler,
            'xiaohongshu': ChineseSocialCrawler,
            'weibo': ChineseSocialCrawler,
            'douyin': ChineseSocialCrawler,
            'bilibili': ChineseSocialCrawler,
        }
        
        crawler_class = crawlers.get(source_type)
        if not crawler_class:
            raise ValueError(f"不支持的社区类型: {source_type}")
        
        return crawler_class(url, config)
```

## 环境变量配置

在 `.env` 文件中添加API凭证：

```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=FoxTrends/1.0

# GitHub API
GITHUB_TOKEN=your_github_token

# Discourse (可选，某些论坛需要)
DISCOURSE_API_USERNAME=your_username
DISCOURSE_API_KEY=your_api_key

# 中文社交媒体 (MediaCrawler配置)
# 已在 MindSpider 中配置
```

## 依赖安装

更新 `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... 现有依赖
    "praw>=7.7.1",              # Reddit
    "PyGithub>=2.1.1",          # GitHub
    "hackernews>=2.0.0",        # HackerNews
    "python-discourse>=1.4.0",  # Discourse
]
```

安装命令:
```bash
cd FoxTrends
uv sync
```

## 实现步骤

### 阶段1: 基础集成 (1-2天)

1. ✅ 创建基础爬虫接口 (`base_crawler.py`)
2. ⬜ 实现Reddit爬虫 (使用PRAW)
3. ⬜ 实现GitHub爬虫 (使用PyGithub)
4. ⬜ 实现HackerNews爬虫
5. ⬜ 创建爬虫工厂

### 阶段2: 数据处理 (1天)

1. ⬜ 统一数据格式转换
2. ⬜ 需求信号提取逻辑
3. ⬜ 情感分析集成
4. ⬜ 热度计算

### 阶段3: 中文社交媒体集成 (2-3天)

1. ⬜ 集成MindSpider的MediaCrawler
2. ⬜ 适配小红书、微博、抖音等平台
3. ⬜ 统一中英文数据格式

### 阶段4: 测试和优化 (1-2天)

1. ⬜ 单元测试
2. ⬜ 集成测试
3. ⬜ 速率限制处理
4. ⬜ 错误重试机制

## API速率限制

各平台的速率限制：

| 平台 | 免费额度 | 限制 |
|------|---------|------|
| Reddit | 60次/分钟 | 需要OAuth |
| GitHub | 5000次/小时 | 需要Token |
| HackerNews | 无限制 | 公开API |
| Discourse | 取决于论坛 | 部分需要认证 |
| 中文社交媒体 | 取决于平台 | 需要登录 |

## 错误处理

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class BaseCrawler:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def fetch_with_retry(self, url):
        """带重试的请求"""
        # 实现请求逻辑
        pass
```

## 数据存储

爬取的数据统一存储到 `demand_signals` 表：

```python
# 数据转换示例
def convert_to_demand_signal(post: Dict) -> DemandSignal:
    """将爬取的帖子转换为需求信号"""
    return DemandSignal(
        title=post['title'],
        content=post['content'],
        source_url=post['url'],
        author=post['author'],
        discussion_count=post['comments_count'],
        sentiment_score=analyze_sentiment(post['content']),
        signal_type=classify_signal_type(post),
        created_at=post['created_at']
    )
```

## 监控和日志

```python
from loguru import logger

class RedditCrawler(BaseCrawler):
    async def fetch_posts(self, limit=50):
        logger.info(f"开始爬取Reddit: {self.community_url}")
        try:
            posts = await self._fetch()
            logger.info(f"成功爬取 {len(posts)} 条帖子")
            return posts
        except Exception as e:
            logger.error(f"爬取失败: {e}")
            raise
```

## 下一步

1. **申请API凭证**：
   - Reddit: https://www.reddit.com/prefs/apps
   - GitHub: https://github.com/settings/tokens

2. **安装依赖**：
   ```bash
   cd FoxTrends
   uv add praw PyGithub hackernews python-discourse
   ```

3. **配置环境变量**：
   - 复制 `.env.example` 到 `.env`
   - 填入API凭证

4. **开始实现**：
   - 从Reddit爬虫开始（最简单）
   - 然后是GitHub和HackerNews
   - 最后集成中文社交媒体

## 参考资源

- PRAW文档: https://praw.readthedocs.io/
- PyGithub文档: https://pygithub.readthedocs.io/
- HackerNews API: https://github.com/HackerNews/API
- MediaCrawler: https://github.com/NanmiCoder/MediaCrawler
- Discourse API: https://docs.discourse.org/

## 注意事项

1. **遵守平台规则**：严格遵守各平台的API使用条款
2. **速率限制**：实现合理的速率限制，避免被封禁
3. **数据隐私**：不采集用户隐私信息
4. **错误处理**：实现完善的错误处理和重试机制
5. **日志记录**：记录详细的爬取日志，便于调试

## 更新日志

- **2025-11-23**: 创建爬虫集成方案文档
- **2025-11-23**: 确定使用成熟开源库而非从头实现
