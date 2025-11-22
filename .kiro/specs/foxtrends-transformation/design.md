# FoxTrends 设计文档

## 概述

FoxTrends 是基于 BettaFish 舆情分析系统深度改造的多垂直社区需求追踪系统。本设计文档详细说明了如何将 BettaFish 的多 Agent 协作架构转化为需求发现和分析平台，同时最大程度复用现有代码和设计模式。

### 核心设计理念

1. **架构继承**: 保留 BettaFish 的 Flask + Multi-Agent 架构
2. **模块复用**: 复用 ForumEngine、ReportEngine、配置系统等核心模块
3. **功能转化**: 将舆情分析能力转化为需求追踪能力
4. **渐进式改造**: 分阶段实施，确保每个阶段都可独立运行
5. **技术栈一致**: 继承 Python + Flask + Streamlit + PostgreSQL 技术栈

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     FoxTrends 主应用 (Flask)                  │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 配置管理      │  │ 数据库管理    │  │ 日志系统      │      │
│  │ (pydantic)   │  │ (PostgreSQL) │  │ (loguru)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│ Community      │   │ Content         │   │ Trend          │
│ Insight Agent  │   │ Analysis Agent  │   │ Discovery Agent│
│                │   │                 │   │                │
│ (InsightEngine)│   │ (MediaEngine)   │   │ (QueryEngine)  │
└───────┬────────┘   └────────┬────────┘   └───────┬────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   ForumEngine     │
                    │  (Agent 协作)      │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│ NicheEngine    │   │ TrendEngine     │   │ ReportEngine   │
│ (社区监控)      │   │ (趋势分析)       │   │ (报告生成)      │
└────────────────┘   └─────────────────┘   └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Dashboard       │
                    │  (前端界面)        │
                    └───────────────────┘
```


### 组件说明

#### 1. Agent 层（改造自 BettaFish）

**CommunityInsightAgent** (改造自 InsightEngine)
- 职责: 分析社区历史数据，识别长期需求模式
- 工具集: 社区数据库查询、需求信号提取、历史趋势对比
- 输入: 社区名称、时间范围、需求关键词
- 输出: 历史需求分析报告、需求演变趋势

**ContentAnalysisAgent** (改造自 MediaEngine)
- 职责: 多模态内容分析，理解用户表达的需求
- 工具集: 文本分析、图片识别、代码片段分析
- 输入: 社区帖子、评论、Issue 内容
- 输出: 需求分类、痛点提取、情感分析

**TrendDiscoveryAgent** (改造自 QueryEngine)
- 职责: 发现当前需求热点，分析需求优先级
- 工具集: 实时搜索、需求检测、竞品分析
- 输入: 需求关键词、竞品信息
- 输出: 需求分析报告、优先级排序、竞品对比

#### 2. 协作层（复用 BettaFish）

**ForumEngine**
- 保持原有的 Agent 协作机制
- 监控各 Agent 的 SummaryNode 输出
- LLM 主持人整合观点并引导讨论
- 输出讨论记录到 forum.log

#### 3. 功能层（新增模块）

**NicheEngine** (社区监控引擎)
- 复用 MindSpider 的爬虫架构
- 支持多种社区数据源（Reddit、Discord、GitHub、HackerNews）
- 实时采集和存储社区数据
- 识别需求信号（痛点、功能请求、问题反馈）

**TrendEngine** (趋势分析引擎)
- 时间序列分析
- 需求热度计算
- 趋势预测模型
- 横向对比分析

**ReportEngine** (复用 BettaFish)
- 保持原有的报告生成机制
- 调整报告模板适应需求分析场景
- 支持多种报告格式（HTML、Markdown、PDF）

#### 4. 展示层（新开发）

**Dashboard**
- 基于 BettaFish 的 Flask + Streamlit 架构
- 社区监控面板
- 需求列表和详情
- 趋势图表和可视化
- 报告导出功能

## 组件和接口

### Agent 接口设计

所有 Agent 继承统一的基类，保持与 BettaFish 一致的接口：

```python
class BaseAgent:
    def __init__(self, config: Settings):
        self.config = config
        self.llm_client = LLMClient(...)
        self.state = State()
        self._initialize_nodes()
    
    def execute_search_tool(self, tool_name: str, query: str, **kwargs):
        """执行搜索工具"""
        pass
    
    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """运行 Agent 主流程"""
        pass
```

### NicheEngine 接口

```python
class NicheEngine:
    def add_community(self, name: str, source_type: str, config: Dict):
        """添加监控社区"""
        pass
    
    def start_monitoring(self, community_id: str):
        """开始监控"""
        pass
    
    def extract_demand_signals(self, content: str) -> List[DemandSignal]:
        """提取需求信号"""
        pass
```

### TrendEngine 接口

```python
class TrendEngine:
    def analyze_trend(self, demand_id: str, time_range: str) -> TrendReport:
        """分析需求趋势"""
        pass
    
    def calculate_hotness(self, demand_id: str) -> float:
        """计算需求热度"""
        pass
    
    def predict_trend(self, demand_id: str, horizon: int) -> Prediction:
        """预测未来趋势"""
        pass
```


## 数据模型

### 核心数据表

#### communities (社区表)
```sql
-- PostgreSQL 版本
CREATE TABLE communities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,  -- reddit, discord, github, hackernews
    source_url TEXT,
    config JSONB,  -- 社区特定配置（PostgreSQL）或 JSON（MySQL）
    status VARCHAR(20) DEFAULT 'active',  -- active, paused, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MySQL 版本使用 AUTO_INCREMENT 和 JSON 类型
-- 注：与 BettaFish 一致，支持 PostgreSQL 和 MySQL 两种数据库
```

#### demand_signals (需求信号表)
```sql
CREATE TABLE demand_signals (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id),
    signal_type VARCHAR(50),  -- pain_point, feature_request, bug_report
    title TEXT NOT NULL,
    content TEXT,
    source_url TEXT,
    author VARCHAR(255),
    sentiment_score FLOAT,  -- -1.0 to 1.0
    hotness_score FLOAT,  -- 0.0 to 100.0
    metadata JSONB,  -- 额外元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### trend_analysis (趋势分析表)
```sql
CREATE TABLE trend_analysis (
    id SERIAL PRIMARY KEY,
    demand_signal_id INTEGER REFERENCES demand_signals(id),
    analysis_date DATE NOT NULL,
    discussion_count INTEGER DEFAULT 0,
    participant_count INTEGER DEFAULT 0,
    sentiment_avg FLOAT,
    hotness_score FLOAT,
    trend_direction VARCHAR(20),  -- rising, stable, declining
    prediction JSONB,  -- 预测数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### agent_discussions (Agent 讨论记录表)
```sql
CREATE TABLE agent_discussions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(50) NOT NULL,  -- community_insight, content_analysis, trend_discovery
    message_type VARCHAR(20),  -- summary, reflection, opinion
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

#### demand_reports (需求报告表)
```sql
CREATE TABLE demand_reports (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    report_type VARCHAR(50),  -- trend_analysis, community_overview, demand_comparison
    content TEXT,
    html_content TEXT,
    communities JSONB,  -- 关联的社区列表
    demand_signals JSONB,  -- 关联的需求信号列表
    generated_by VARCHAR(50),  -- 生成者（system, user）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 数据关系

- communities 1:N demand_signals
- demand_signals 1:N trend_analysis
- demand_signals N:M demand_reports (通过 JSONB 字段关联)


## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

基于需求分析，以下是 FoxTrends 系统的核心正确性属性：

### 属性 1: 配置加载一致性
*对于任何*有效的 .env 文件，系统加载的配置值应该与文件中定义的值完全一致
**验证需求: 1.2**

### 属性 2: 数据库连接配置兼容性
*对于任何*有效的数据库配置（PostgreSQL 或 MySQL），FoxTrends 应该能够使用与 BettaFish 相同的配置参数成功建立连接
**验证需求: 1.5**

### 属性 3: ForumEngine 协作机制保留
*对于任何*Agent 生成的 SummaryNode 输出，ForumEngine 应该能够正确监控、记录并触发主持人发言
**验证需求: 2.4**

### 属性 4: Agent 节点模式一致性
*对于任何*Agent 的执行流程，应该包含 FirstSummaryNode 和 ReflectionSummaryNode 节点，并按照 BettaFish 的模式生成输出
**验证需求: 2.5**

### 属性 5: 多社区管理
*对于任何*数量的社区添加操作，NicheEngine 应该能够正确存储所有社区信息，并且每个社区都有唯一的标识符
**验证需求: 3.1**

### 属性 6: 数据采集完整性
*对于任何*社区数据采集任务，采集的数据应该完整存储到数据库，并且数据结构符合预定义的 schema
**验证需求: 3.2, 3.3**

### 属性 7: 需求信号分类正确性
*对于任何*包含需求信号的内容，NicheEngine 应该能够将其正确分类为痛点、功能请求或问题反馈之一
**验证需求: 3.4**

### 属性 8: 监控状态一致性
*对于任何*监控状态更新操作，系统返回的状态应该与数据库中存储的状态一致
**验证需求: 3.5**

### 属性 9: 时间序列模式识别
*对于任何*具有明显趋势的时间序列数据，TrendEngine 应该能够识别出上升、稳定或下降的模式
**验证需求: 4.1**

### 属性 10: 热度计算单调性
*对于任何*需求，如果讨论频率、参与人数或情感倾向增加，则计算的热度分数不应该减少
**验证需求: 4.2**

### 属性 11: 需求对比完整性
*对于任何*多个需求的对比请求，TrendEngine 应该为每个需求生成对比维度的数据，并且所有需求使用相同的对比维度
**验证需求: 4.4**

### 属性 12: 趋势报告结构化
*对于任何*趋势分析请求，生成的报告应该包含预定义的所有必需字段（时间范围、趋势方向、热度分数等）
**验证需求: 4.5**

### 属性 13: 需求列表排序正确性
*对于任何*需求列表查询，返回的列表应该按照热度分数降序排列
**验证需求: 5.3**

### 属性 14: 报告生成幂等性
*对于任何*相同的输入参数，多次调用报告生成功能应该产生内容一致的报告
**验证需求: 5.5**

### 属性 15: Agent 发言记录完整性
*对于任何*Agent 的 SummaryNode 输出，ForumEngine 应该将其完整记录到 forum.log，并且记录包含时间戳和 Agent 标识
**验证需求: 6.1**

### 属性 16: 讨论记录持久化
*对于任何*ForumEngine 的讨论会话，所有 Agent 发言和主持人总结应该被持久化到 forum.log 文件
**验证需求: 6.5**

### 属性 17: LLM 配置独立性
*对于任何*Agent，修改其 LLM 配置不应该影响其他 Agent 的 LLM 配置
**验证需求: 7.2**

### 属性 18: 数据库配置向后兼容
*对于任何*BettaFish 的有效数据库配置，FoxTrends 应该能够使用相同的配置成功连接数据库
**验证需求: 7.3**

### 属性 19: 外键约束完整性
*对于任何*父表记录的删除操作，如果存在子表记录引用该父记录，则删除操作应该失败或级联删除子记录（取决于外键配置）
**验证需求: 8.4**


## 错误处理

### 错误分类

#### 1. 配置错误
- 缺少必需的配置项（API Key、数据库连接信息）
- 配置格式错误（无效的 URL、端口号）
- 处理策略: 启动时验证配置，提供清晰的错误消息，拒绝启动

#### 2. 数据库错误
- 连接失败
- 查询超时
- 数据完整性约束违反
- 处理策略: 使用连接池和重试机制，记录详细错误日志，提供降级方案

#### 3. Agent 执行错误
- LLM API 调用失败
- 搜索工具超时
- 节点处理异常
- 处理策略: 实现重试机制（使用 tenacity），记录错误上下文，提供部分结果

#### 4. 数据采集错误
- 社区数据源不可访问
- 爬虫被限流或封禁
- 数据解析失败
- 处理策略: 实现指数退避重试，记录失败的采集任务，支持手动重试

#### 5. ForumEngine 错误
- 日志文件写入失败
- 主持人 LLM 调用失败
- Agent 输出解析错误
- 处理策略: 使用文件锁防止并发写入冲突，降级到无主持人模式，容错解析

### 错误恢复策略

#### 优雅降级
- Agent 执行失败时，返回部分结果而不是完全失败
- ForumEngine 主持人失败时，继续记录 Agent 发言
- 报告生成失败时，提供简化版本

#### 状态恢复
- 使用数据库事务确保数据一致性
- 记录 Agent 执行状态，支持从中断点恢复
- 保存中间结果，避免重复计算

#### 监控和告警
- 记录所有错误到日志系统（loguru）
- 关键错误触发告警（可选集成告警系统）
- 提供健康检查端点

## 测试策略

### 单元测试

#### Agent 测试
- 测试每个 Agent 的初始化
- 测试节点的独立功能
- 测试工具集的调用
- 使用 mock 隔离外部依赖

#### NicheEngine 测试
- 测试社区添加和管理
- 测试需求信号提取逻辑
- 测试数据存储功能
- 使用测试数据库

#### TrendEngine 测试
- 测试热度计算公式
- 测试趋势识别算法
- 测试对比分析逻辑
- 使用固定的测试数据

### 属性测试

使用 Hypothesis 库进行属性测试，验证系统的通用属性：

#### 配置属性测试
```python
@given(st.dictionaries(st.text(), st.text()))
def test_config_loading_consistency(config_dict):
    """属性 1: 配置加载一致性"""
    # 生成随机配置，验证加载后的值与输入一致
```

#### 数据库属性测试
```python
@given(st.lists(st.builds(Community)))
def test_multi_community_management(communities):
    """属性 5: 多社区管理"""
    # 添加多个社区，验证都能正确存储且有唯一 ID
```

#### 排序属性测试
```python
@given(st.lists(st.builds(DemandSignal)))
def test_demand_list_sorting(demands):
    """属性 13: 需求列表排序正确性"""
    # 生成随机需求列表，验证返回的列表按热度降序排列
```

### 集成测试

#### ForumEngine 集成测试
- 启动多个 Agent
- 验证 ForumEngine 能够监控所有 Agent 的输出
- 验证主持人发言在适当时机生成
- 验证讨论记录完整性

#### 端到端测试
- 模拟完整的需求分析流程
- 从社区监控到报告生成
- 验证所有组件协同工作
- 使用测试数据库和 mock 外部 API

### 测试覆盖目标

- 单元测试覆盖率: 80%+
- 属性测试: 覆盖所有核心正确性属性
- 集成测试: 覆盖主要用户场景
- 端到端测试: 至少 3 个完整流程

### 测试工具

- **pytest**: 测试框架
- **pytest-cov**: 覆盖率报告
- **Hypothesis**: 属性测试
- **pytest-mock**: Mock 工具
- **pytest-asyncio**: 异步测试支持


## 实施计划

### 阶段 1: 基础架构迁移 (Week 1-2)

#### 目标
建立 FoxTrends 的基础架构，确保与 BettaFish 的兼容性

#### 任务
1. 创建项目结构，复制 BettaFish 的核心文件
2. 配置 UV 依赖管理（pyproject.toml, uv.lock）
3. 迁移配置系统（config.py, .env.example）
4. 迁移数据库连接和初始化代码
5. 迁移 Flask 主应用（app.py）
6. 迁移 ForumEngine（monitor.py, llm_host.py）
7. 迁移 ReportEngine
8. 验证基础架构可以正常启动

#### 验收标准
- UV 可以成功安装所有依赖
- 配置系统可以正确加载 .env 文件
- 数据库连接成功
- Flask 应用可以启动
- ForumEngine 可以监控日志文件

### 阶段 2: Agent 系统重构 (Week 3-4)

#### 目标
将 BettaFish 的 Agent 改造为需求追踪 Agent

#### 任务
1. 重构 InsightEngine 为 CommunityInsightAgent
   - 修改工具集适应社区数据查询
   - 调整 prompt 适应需求分析场景
   - 保留节点结构和协作机制
2. 重构 MediaEngine 为 ContentAnalysisAgent
   - 调整多模态分析逻辑
   - 适配社区内容格式
3. 重构 QueryEngine 为 TrendDiscoveryAgent
   - 调整搜索策略
   - 增加趋势发现逻辑
4. 验证 Agent 与 ForumEngine 的协作

#### 验收标准
- 三个 Agent 可以独立运行
- Agent 输出符合需求分析场景
- ForumEngine 可以正确监控 Agent 输出
- 主持人可以生成需求分析相关的总结

### 阶段 3: NicheEngine 开发 (Week 5-6)

#### 目标
开发社区监控引擎，实现数据采集功能

#### 任务
1. 设计和创建数据库表（communities, demand_signals）
2. 实现社区管理功能（添加、删除、更新）
3. 复用 MindSpider 架构实现爬虫
   - 适配 Reddit API
   - 适配 GitHub Issues API
   - 适配 HackerNews API
4. 实现需求信号提取逻辑
5. 实现监控状态管理
6. 编写单元测试和集成测试

#### 验收标准
- 可以添加和管理多个社区
- 爬虫可以成功采集数据
- 需求信号可以正确分类
- 数据完整存储到数据库
- 测试覆盖率达到 80%+

### 阶段 4: TrendEngine 开发 (Week 7-8)

#### 目标
开发趋势分析引擎，实现需求分析功能

#### 任务
1. 创建 trend_analysis 表
2. 实现时间序列分析算法
3. 实现热度计算公式
4. 实现趋势预测模型（简单统计模型）
5. 实现横向对比分析
6. 实现趋势报告生成
7. 编写单元测试和属性测试

#### 验收标准
- 可以识别时间序列变化模式
- 热度计算符合预期
- 趋势预测返回合理结果
- 对比分析包含所有维度
- 报告结构完整
- 属性测试覆盖核心属性

### 阶段 5: Dashboard 开发 (Week 9-10)

#### 目标
开发前端界面，提供用户交互

#### 任务
1. 设计 Dashboard 布局（基于 BettaFish 风格）
2. 实现社区监控面板
3. 实现需求列表和详情页
4. 实现趋势图表（使用 plotly）
5. 实现报告导出功能
6. 集成 Flask API 端点
7. 编写前端测试

#### 验收标准
- Dashboard 可以正常访问
- 所有功能模块可以正常使用
- 图表正确展示数据
- 报告可以成功导出
- UI 风格与 BettaFish 一致

### 阶段 6: 集成测试和优化 (Week 11-12)

#### 目标
完成系统集成，进行端到端测试和性能优化

#### 任务
1. 编写端到端测试
2. 进行性能测试和优化
3. 完善错误处理和日志
4. 编写文档（README, 配置指南, 开发文档）
5. 准备示例配置和运行案例
6. 进行用户验收测试

#### 验收标准
- 端到端测试通过
- 系统性能满足要求
- 文档完整清晰
- 示例可以成功运行
- 用户反馈积极

## 技术栈

### 后端
- **Python 3.11+**: 主要编程语言
- **Flask 2.3+**: Web 框架
- **Flask-SocketIO**: WebSocket 支持
- **Pydantic 2.5+**: 配置管理和数据验证
- **SQLAlchemy 2.0+**: ORM
- **PostgreSQL / MySQL**: 数据库（与 BettaFish 一致，通过 DB_DIALECT 配置选择）
- **UV**: 包管理工具

### Agent 和 LLM
- **OpenAI API**: LLM 接口（兼容多种提供商）
- **Loguru**: 日志系统
- **Tenacity**: 重试机制

### 数据采集
- **Playwright**: 浏览器自动化
- **aiohttp**: 异步 HTTP 客户端
- **BeautifulSoup4**: HTML 解析

### 前端
- **Streamlit**: 快速原型和子应用
- **Plotly**: 数据可视化
- **HTML/CSS/JavaScript**: Dashboard 前端

### 测试
- **pytest**: 测试框架
- **Hypothesis**: 属性测试
- **pytest-cov**: 覆盖率
- **pytest-mock**: Mock 工具

### 部署
- **Docker**: 容器化
- **Docker Compose**: 多容器编排

## 性能考虑

### 数据库优化
- 为常用查询字段添加索引（community_id, created_at, hotness_score）
- 使用连接池管理数据库连接
- 对大表进行分区（按时间分区 trend_analysis）

### Agent 并发
- 使用异步 I/O 处理 LLM 调用
- 实现请求队列避免过载
- 使用缓存减少重复计算

### 数据采集优化
- 实现增量采集，避免重复抓取
- 使用分布式任务队列（可选 Celery）
- 实现限流机制遵守 API 限制

### 前端性能
- 使用分页加载大量数据
- 实现数据缓存
- 异步加载图表数据

## 安全考虑

### API 安全
- 使用环境变量存储敏感信息
- 实现 API 密钥轮换机制
- 限制 API 调用频率

### 数据安全
- 使用参数化查询防止 SQL 注入
- 实现输入验证和清理
- 加密存储敏感数据（可选）

### 访问控制
- 实现用户认证（可选）
- 基于角色的访问控制（可选）
- 审计日志记录

## 可扩展性

### 新增社区数据源
- 定义统一的数据源接口
- 实现插件化的爬虫系统
- 支持自定义数据源配置

### 新增 Agent
- 遵循 BaseAgent 接口
- 注册到 ForumEngine
- 配置独立的 LLM 和工具集

### 新增分析维度
- 扩展 TrendEngine 的分析算法
- 添加新的数据表字段
- 更新 Dashboard 展示

## 维护和监控

### 日志管理
- 使用 loguru 统一日志格式
- 按级别和模块分类日志
- 定期清理旧日志文件

### 监控指标
- Agent 执行成功率
- 数据采集成功率
- API 响应时间
- 数据库查询性能

### 备份策略
- 定期备份数据库
- 备份配置文件
- 备份生成的报告

