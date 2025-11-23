# FoxTrends 开发文档

## 目录

1. [代码结构说明](#代码结构说明)
2. [Agent 扩展指南](#agent-扩展指南)
3. [数据源扩展指南](#数据源扩展指南)
4. [API 文档](#api-文档)

---

## 代码结构说明

### 项目架构

FoxTrends 采用模块化架构，主要由以下几个核心模块组成：

```
FoxTrends/
├── CommunityInsightAgent/    # 社区洞察 Agent
├── ContentAnalysisAgent/      # 内容分析 Agent
├── NicheEngine/               # 社区监控引擎
├── ForumEngine/               # Agent 协作引擎
├── ReportEngine/              # 报告生成引擎
├── Dashboard/                 # Web Dashboard
├── database/                  # 数据库管理
├── utils/                     # 工具函数
├── templates/                 # HTML 模板
├── tests/                     # 测试代码
├── app.py                     # Flask 主应用
└── config.py                  # 配置管理
```

### 核心模块详解

#### 1. CommunityInsightAgent

**功能**: 分析社区历史数据，识别需求模式和趋势

**主要文件**:
- `agent.py`: Agent 主逻辑，定义工作流
- `nodes/`: 处理节点
  - `first_summary_node.py`: 初始分析节点
  - `reflection_summary_node.py`: 反思总结节点
- `state.py`: Agent 状态管理
- `tools/`: Agent 工具集
  - `database_query.py`: 数据库查询工具
  - `pattern_recognition.py`: 模式识别工具

**工作流程**:
```
输入 → FirstSummaryNode → ReflectionSummaryNode → 输出
```

#### 2. ContentAnalysisAgent

**功能**: 分析社区内容，提取需求信号

**主要文件**:
- `agent.py`: Agent 主逻辑
- `nodes/`: 处理节点
  - `content_analysis_node.py`: 内容分析节点
  - `classification_node.py`: 分类节点
- `tools/`: Agent 工具集
  - `text_analyzer.py`: 文本分析工具
  - `code_analyzer.py`: 代码分析工具

#### 3. NicheEngine

**功能**: 社区监控和数据采集引擎

**主要文件**:
- `engine.py`: 监控引擎主逻辑
- `models.py`: 数据模型（Community, DemandSignal）
- `crawlers/`: 爬虫适配器
  - `reddit_crawler.py`: Reddit 爬虫
  - `github_crawler.py`: GitHub Issues 爬虫
  - `hackernews_crawler.py`: HackerNews 爬虫
- `signal_extractor.py`: 需求信号提取器

**数据流**:
```
社区配置 → 爬虫采集 → 信号提取 → 数据存储 → Agent 分析
```

#### 4. ForumEngine

**功能**: Agent 协作和讨论管理

**主要文件**:
- `monitor.py`: 日志监控和讨论管理
- `llm_host.py`: LLM 主持人模块

**协作流程**:
```
Agent 输出 → 日志监控 → 主持人总结 → 新一轮讨论
```

#### 5. ReportEngine

**功能**: 生成分析报告

**主要文件**:
- `engine.py`: 报告生成引擎
- `templates/`: 报告模板

---

## Agent 扩展指南

### 创建新 Agent

#### 步骤 1: 创建 Agent 目录结构

```bash
mkdir -p FoxTrends/YourAgent/{nodes,tools}
touch FoxTrends/YourAgent/{__init__.py,agent.py,state.py}
```

#### 步骤 2: 定义 Agent 状态

在 `state.py` 中定义 Agent 的状态结构：

```python
from typing import TypedDict, List, Optional

class YourAgentState(TypedDict):
    """Your Agent 状态定义"""
    input_data: str
    analysis_result: Optional[str]
    insights: List[str]
    error: Optional[str]
```

#### 步骤 3: 实现处理节点

在 `nodes/` 目录下创建处理节点：

```python
# nodes/analysis_node.py
from typing import Dict, Any
from ..state import YourAgentState

def analysis_node(state: YourAgentState) -> Dict[str, Any]:
    """分析节点"""
    input_data = state.get("input_data", "")
    
    # 实现你的分析逻辑
    result = perform_analysis(input_data)
    
    return {
        "analysis_result": result,
        "insights": extract_insights(result)
    }
```

#### 步骤 4: 创建 Agent 工具

在 `tools/` 目录下创建工具：

```python
# tools/your_tool.py
from typing import Any

class YourTool:
    """Your Tool 工具类"""
    
    def __init__(self, config: dict):
        self.config = config
    
    def execute(self, input_data: Any) -> Any:
        """执行工具逻辑"""
        # 实现工具功能
        pass
```

#### 步骤 5: 实现 Agent 主逻辑

在 `agent.py` 中实现 Agent：

```python
# agent.py
from langgraph.graph import StateGraph, END
from .state import YourAgentState
from .nodes.analysis_node import analysis_node

class YourAgent:
    """Your Agent 类"""
    
    def __init__(self, config: dict):
        self.config = config
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建 Agent 工作流图"""
        workflow = StateGraph(YourAgentState)
        
        # 添加节点
        workflow.add_node("analysis", analysis_node)
        
        # 定义边
        workflow.set_entry_point("analysis")
        workflow.add_edge("analysis", END)
        
        return workflow.compile()
    
    def run(self, input_data: str) -> dict:
        """运行 Agent"""
        initial_state = {
            "input_data": input_data,
            "analysis_result": None,
            "insights": [],
            "error": None
        }
        
        result = self.graph.invoke(initial_state)
        return result
```

#### 步骤 6: 集成到 ForumEngine

在 `app.py` 中注册新 Agent：

```python
from FoxTrends.YourAgent.agent import YourAgent

# 初始化 Agent
your_agent = YourAgent(config)

# 添加到 Agent 列表
agents = {
    "insight": community_insight_agent,
    "content": content_analysis_agent,
    "your_agent": your_agent  # 新增
}
```

### Agent 最佳实践

1. **状态管理**: 使用 TypedDict 明确定义状态结构
2. **错误处理**: 在每个节点中添加 try-except 错误处理
3. **日志记录**: 使用 loguru 记录关键操作和错误
4. **工具复用**: 将通用功能抽象为工具类
5. **测试覆盖**: 为每个节点和工具编写单元测试

---

## 数据源扩展指南

### 添加新数据源

#### 步骤 1: 创建爬虫适配器

在 `NicheEngine/crawlers/` 目录下创建新爬虫：

```python
# crawlers/your_platform_crawler.py
from typing import List, Dict, Any
import aiohttp
from loguru import logger

class YourPlatformCrawler:
    """Your Platform 爬虫"""
    
    def __init__(self, config: dict):
        self.api_key = config.get("api_key")
        self.base_url = "https://api.yourplatform.com"
    
    async def fetch_data(self, community_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取数据"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/communities/{community_id}/posts"
                params = {"limit": limit, "api_key": self.api_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_data(data)
                    else:
                        logger.error(f"API 请求失败: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"数据获取失败: {e}")
            return []
    
    def _parse_data(self, raw_data: dict) -> List[Dict[str, Any]]:
        """解析数据"""
        posts = []
        for item in raw_data.get("items", []):
            post = {
                "title": item.get("title"),
                "content": item.get("body"),
                "author": item.get("author", {}).get("username"),
                "created_at": item.get("created_at"),
                "url": item.get("url"),
                "score": item.get("score", 0),
                "comments_count": item.get("comments_count", 0)
            }
            posts.append(post)
        return posts
```

#### 步骤 2: 注册爬虫

在 `NicheEngine/engine.py` 中注册爬虫：

```python
from .crawlers.your_platform_crawler import YourPlatformCrawler

class NicheEngine:
    def __init__(self, config: dict):
        self.crawlers = {
            "reddit": RedditCrawler(config),
            "github": GitHubCrawler(config),
            "hackernews": HackerNewsCrawler(config),
            "yourplatform": YourPlatformCrawler(config)  # 新增
        }
```

#### 步骤 3: 更新数据库模型

如果需要存储平台特定的数据，更新 `database/models.py`：

```python
class Community(Base):
    __tablename__ = "communities"
    
    # ... 现有字段 ...
    
    # 添加平台特定配置
    platform_config = Column(JSON, nullable=True)
```

#### 步骤 4: 配置数据源

在 `.env` 文件中添加配置：

```bash
# Your Platform 配置
YOURPLATFORM_API_KEY=your_api_key_here
YOURPLATFORM_BASE_URL=https://api.yourplatform.com
```

### 数据源最佳实践

1. **异步请求**: 使用 aiohttp 进行异步 HTTP 请求
2. **速率限制**: 实现请求速率限制，避免被封禁
3. **错误重试**: 添加重试机制处理临时性错误
4. **数据验证**: 验证爬取的数据格式和完整性
5. **增量更新**: 支持增量数据更新，避免重复爬取

---

## API 文档

### 系统状态 API

#### GET /api/system/status

获取系统状态

**响应**:
```json
{
  "success": true,
  "status": {
    "database": "connected",
    "agents": {
      "insight": "ready",
      "content": "ready"
    },
    "forum_engine": "active",
    "report_engine": "ready"
  }
}
```

### 社区管理 API

#### GET /api/communities

获取社区列表

**参数**:
- `status` (可选): 筛选状态 (active/inactive)
- `limit` (可选): 返回数量限制

**响应**:
```json
{
  "success": true,
  "communities": [
    {
      "id": 1,
      "name": "r/python",
      "source_type": "reddit",
      "status": "active",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### POST /api/communities

添加新社区

**请求体**:
```json
{
  "name": "r/python",
  "source_type": "reddit",
  "source_url": "https://reddit.com/r/python",
  "config": {
    "keywords": ["bug", "feature request"]
  }
}
```

**响应**:
```json
{
  "success": true,
  "community_id": 1,
  "message": "社区添加成功"
}
```

#### DELETE /api/communities/{id}

删除社区

**响应**:
```json
{
  "success": true,
  "message": "社区删除成功"
}
```

### 需求管理 API

#### GET /api/demands

获取需求列表

**参数**:
- `community_id` (可选): 筛选社区
- `signal_type` (可选): 筛选类型 (pain_point/feature_request/bug_report)
- `limit` (可选): 返回数量限制
- `sort_by` (可选): 排序字段 (hotness_score/created_at)

**响应**:
```json
{
  "success": true,
  "demands": [
    {
      "id": 1,
      "title": "需求标题",
      "content": "需求内容",
      "signal_type": "pain_point",
      "hotness_score": 85.5,
      "sentiment_score": 0.7,
      "community_id": 1,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### GET /api/demands/{id}

获取需求详情

**响应**:
```json
{
  "success": true,
  "demand": {
    "id": 1,
    "title": "需求标题",
    "content": "需求内容",
    "signal_type": "pain_point",
    "hotness_score": 85.5,
    "sentiment_score": 0.7,
    "author": "user123",
    "source_url": "https://...",
    "discussion_count": 42,
    "participant_count": 15,
    "community": {
      "id": 1,
      "name": "r/python"
    },
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 分析 API

#### GET /api/analysis/metrics

获取分析指标

**参数**:
- `days` (可选): 时间范围（天数），默认 30

**响应**:
```json
{
  "success": true,
  "metrics": {
    "total_demands": 150,
    "avg_hotness": 72.5,
    "avg_sentiment": 0.65,
    "active_communities": 5
  }
}
```

#### GET /api/analysis/trend

获取趋势数据

**参数**:
- `days` (可选): 时间范围（天数），默认 30
- `view` (可选): 视图类型 (hotness/sentiment/count)

**响应**:
```json
{
  "success": true,
  "trend_data": {
    "dates": ["2024-01-01", "2024-01-02"],
    "values": [75.5, 78.2]
  }
}
```

#### GET /api/analysis/type-distribution

获取类型分布

**参数**:
- `days` (可选): 时间范围（天数），默认 30

**响应**:
```json
{
  "success": true,
  "distribution": [
    {"type": "pain_point", "count": 50},
    {"type": "feature_request", "count": 30},
    {"type": "bug_report", "count": 20}
  ]
}
```

#### GET /api/analysis/pain-points

获取热门痛点

**参数**:
- `days` (可选): 时间范围（天数），默认 30
- `limit` (可选): 返回数量限制，默认 10

**响应**:
```json
{
  "success": true,
  "pain_points": [
    {
      "title": "痛点标题",
      "hotness_score": 95.5,
      "community": "r/python"
    }
  ]
}
```

### 报告 API

#### POST /api/reports/generate

生成分析报告

**请求体**:
```json
{
  "community_ids": [1, 2],
  "time_range": 30,
  "include_insights": true
}
```

**响应**:
```json
{
  "success": true,
  "report_id": "report_20240101_123456",
  "report_url": "/reports/report_20240101_123456.html"
}
```

#### GET /api/reports

获取报告列表

**响应**:
```json
{
  "success": true,
  "reports": [
    {
      "id": "report_20240101_123456",
      "created_at": "2024-01-01T12:34:56",
      "url": "/reports/report_20240101_123456.html"
    }
  ]
}
```

### Dashboard API

#### GET /api/dashboard/stats

获取 Dashboard 统计数据

**响应**:
```json
{
  "success": true,
  "stats": {
    "total_communities": 5,
    "total_demands": 150,
    "active_communities": 3,
    "today_demands": 12
  }
}
```

### 错误响应格式

所有 API 在发生错误时返回统一格式：

```json
{
  "success": false,
  "error": "错误信息描述"
}
```

常见 HTTP 状态码：
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 开发工具

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_niche_engine.py

# 运行带覆盖率的测试
uv run pytest --cov=FoxTrends --cov-report=html

# 运行属性测试
uv run pytest tests/property_tests/
```

### 代码格式化

```bash
# 格式化代码
uv run black FoxTrends/

# 检查代码风格
uv run flake8 FoxTrends/
```

### 数据库管理

```bash
# 初始化数据库
uv run python database/init_database.py

# 重置数据库
uv run python database/init_database.py --reset
```

### 日志查看

```bash
# 查看实时日志
tail -f logs/foxtrends.log

# 查看 Agent 日志
tail -f logs/agents.log

# 查看 Forum 日志
tail -f logs/forum.log
```

---

## 贡献指南

### 提交代码

1. Fork 项目
2. 创建特性分支: `git checkout -b feature/your-feature`
3. 提交更改: `git commit -am 'Add some feature'`
4. 推送分支: `git push origin feature/your-feature`
5. 提交 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型提示
- 编写文档字符串
- 添加单元测试
- 保持代码简洁

### 测试要求

- 新功能必须包含单元测试
- 核心功能需要属性测试
- 集成测试覆盖主要流程
- 测试覆盖率不低于 80%

---

## 常见问题

### Q: 如何添加新的 LLM 提供商？

A: 在 `config.py` 中添加新的 LLM 配置，然后在 Agent 中使用相应的 API 密钥和端点。

### Q: 如何自定义报告模板？

A: 在 `ReportEngine/templates/` 目录下创建新的 HTML 模板，然后在报告生成时指定模板名称。

### Q: 如何优化爬虫性能？

A: 使用异步请求、实现请求池、添加缓存机制、使用增量更新策略。

### Q: 如何扩展需求信号类型？

A: 在 `NicheEngine/signal_extractor.py` 中添加新的分类逻辑，并更新数据库模型。

---

## 更多资源

- [项目 README](../README.md)
- [配置指南](../docs/CONFIGURATION.md)
- [部署指南](../docs/DEPLOYMENT.md)
- [API 参考](../docs/API.md)

---

**最后更新**: 2024-11-23
