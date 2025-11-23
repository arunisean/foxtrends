# 真实数据采集功能实现计划

## 当前状态

- ✅ 系统架构已完成
- ✅ 数据库设计已完成
- ✅ Dashboard UI已完成
- ✅ Mock数据生成已禁用
- ⬜ **真实数据采集功能待实现**

## 实现方案

使用成熟的开源爬虫库，而不是从头实现：

| 平台 | 开源库 | 状态 |
|------|--------|------|
| Reddit | PRAW | ⬜ 待实现 |
| GitHub | PyGithub | ⬜ 待实现 |
| HackerNews | hackernews | ⬜ 待实现 |
| Discourse | python-discourse | ⬜ 待实现 |
| 小红书/微博等 | MediaCrawler (已有) | ⬜ 待集成 |

## 实现步骤

### 第1步：安装依赖 (5分钟)

```bash
cd FoxTrends
uv sync  # 会自动安装新添加的依赖
```

### 第2步：申请API凭证 (10-15分钟)

1. **Reddit**:
   - 访问 https://www.reddit.com/prefs/apps
   - 创建应用，选择"script"类型
   - 获取 client_id 和 client_secret

2. **GitHub**:
   - 访问 https://github.com/settings/tokens
   - 创建Personal Access Token
   - 权限选择：public_repo, read:user

3. **HackerNews**:
   - 无需认证，公开API

### 第3步：配置环境变量 (2分钟)

在 `.env` 文件中添加：

```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=FoxTrends/1.0

# GitHub API
GITHUB_TOKEN=your_github_token_here
```

### 第4步：实现爬虫 (2-3小时)

按优先级实现：

1. **Reddit爬虫** (最简单，30分钟)
   - 文件：`FoxTrends/NicheEngine/crawlers/reddit_crawler.py`
   - 使用PRAW库
   - 支持获取subreddit的帖子

2. **GitHub爬虫** (中等，45分钟)
   - 文件：`FoxTrends/NicheEngine/crawlers/github_crawler.py`
   - 使用PyGithub库
   - 支持获取Issues和Discussions

3. **HackerNews爬虫** (简单，30分钟)
   - 文件：`FoxTrends/NicheEngine/crawlers/hackernews_crawler.py`
   - 使用hackernews库
   - 支持获取热门故事

4. **爬虫工厂** (30分钟)
   - 文件：`FoxTrends/NicheEngine/crawlers/factory.py`
   - 根据社区类型创建对应爬虫

### 第5步：集成到监控任务 (30分钟)

修改 `FoxTrends/NicheEngine/monitoring_task.py`：

```python
from NicheEngine.crawlers.factory import CrawlerFactory

class MonitoringTask:
    USE_MOCK_DATA = False  # 改为False启用真实采集
    
    async def collect_data(self):
        """使用真实爬虫采集数据"""
        crawler = CrawlerFactory.create_crawler(
            self.community.source_type,
            self.community.source_url,
            self.community.config
        )
        return await crawler.crawl(limit=50)
```

### 第6步：测试 (30分钟)

1. 添加一个Reddit社区（如r/python）
2. 启动监控
3. 查看是否能采集到真实数据
4. 检查数据库中的需求信号

## 快速开始（最小可行方案）

如果时间紧迫，可以先实现Reddit爬虫：

### 1. 安装依赖
```bash
cd FoxTrends
uv add praw
```

### 2. 创建Reddit爬虫

创建文件 `FoxTrends/NicheEngine/crawlers/reddit_crawler.py`:

```python
import praw
from typing import List, Dict, Any
from datetime import datetime
import os

class RedditCrawler:
    def __init__(self, subreddit_name: str):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'FoxTrends/1.0')
        )
        self.subreddit = self.reddit.subreddit(subreddit_name)
    
    def fetch_posts(self, limit=50) -> List[Dict[str, Any]]:
        posts = []
        for submission in self.subreddit.hot(limit=limit):
            posts.append({
                'id': submission.id,
                'title': submission.title,
                'content': submission.selftext,
                'author': str(submission.author),
                'url': f"https://reddit.com{submission.permalink}",
                'score': submission.score,
                'comments_count': submission.num_comments,
                'created_at': datetime.fromtimestamp(submission.created_utc)
            })
        return posts
```

### 3. 在监控任务中使用

修改 `monitoring_task.py` 的 `collect_data()` 方法：

```python
def collect_data(self):
    if self.community.source_type == 'reddit':
        from NicheEngine.crawlers.reddit_crawler import RedditCrawler
        # 从URL提取subreddit名称
        subreddit_name = self.community.source_url.split('/r/')[-1].strip('/')
        crawler = RedditCrawler(subreddit_name)
        return crawler.fetch_posts(limit=50)
    else:
        # 其他类型暂时返回空
        return []
```

### 4. 启用真实采集

修改 `monitoring_task.py`:
```python
USE_MOCK_DATA = False  # 改为False
```

### 5. 测试

```bash
# 启动应用
cd FoxTrends
uv run python app.py

# 在Dashboard中添加Reddit社区
# 例如：r/python
# URL: https://reddit.com/r/python
```

## 预期效果

实现后，系统将能够：

1. ✅ 从Reddit采集真实的帖子数据
2. ✅ 提取标题、内容、作者、评论数等信息
3. ✅ 根据关键词过滤相关讨论
4. ✅ 存储到数据库的demand_signals表
5. ✅ 在Dashboard中显示真实的需求信号

## 注意事项

1. **API限制**：
   - Reddit: 60次/分钟
   - GitHub: 5000次/小时
   - 需要实现速率限制

2. **错误处理**：
   - 网络错误重试
   - API限制处理
   - 认证失败处理

3. **数据质量**：
   - 去重处理
   - 内容过滤
   - 情感分析

## 后续优化

1. 添加更多平台支持
2. 实现增量采集（只采集新数据）
3. 添加数据清洗和预处理
4. 实现智能调度（根据社区活跃度调整采集频率）
5. 集成中文社交媒体（小红书、微博等）

## 参考文档

- [爬虫集成方案](./CRAWLER_INTEGRATION.md)
- [PRAW文档](https://praw.readthedocs.io/)
- [PyGithub文档](https://pygithub.readthedocs.io/)

## 时间估算

| 任务 | 预计时间 |
|------|---------|
| 安装依赖 | 5分钟 |
| 申请API凭证 | 15分钟 |
| 实现Reddit爬虫 | 30分钟 |
| 集成到监控任务 | 30分钟 |
| 测试和调试 | 30分钟 |
| **总计** | **约2小时** |

## 更新日志

- **2025-11-23**: 创建实现计划文档
- **2025-11-23**: 确定使用开源库的方案
