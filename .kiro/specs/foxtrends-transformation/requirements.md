# FoxTrends 需求文档

## 简介

FoxTrends 是基于 BettaFish 舆情分析系统深度改造的多垂直社区需求追踪系统。该系统复用 BettaFish 的多 Agent 协作机制，将原有的舆情分析能力转化为垂直社区（niche communities）的需求发现和分析能力。系统继承 BettaFish 的技术栈，采用 UV 进行依赖管理，最大程度借鉴现有代码和设计模式。

## 术语表

- **FoxTrends**: 基于 BettaFish 改造的多垂直社区需求追踪系统
- **BettaFish**: 原有的多智能体舆情分析系统
- **Niche Community**: 垂直社区，指特定领域或兴趣的小众社区
- **Agent**: 智能代理，系统中的独立分析单元
- **ForumEngine**: 论坛引擎，负责 Agent 间的协作和讨论管理
- **NicheEngine**: 垂直社区监控引擎，新增的社区数据采集和分析模块
- **UV**: Python 包管理工具，用于依赖管理
- **Dashboard**: 仪表板，系统的前端展示界面
- **MindSpider**: BettaFish 的爬虫系统，用于数据采集

## 需求

### 需求 1: 系统架构迁移

**用户故事**: 作为系统架构师，我希望将 BettaFish 的核心架构迁移到 FoxTrends，以便复用成熟的多 Agent 协作机制。

#### 验收标准

1. WHEN 系统启动时 THEN FoxTrends SHALL 保留 BettaFish 的 Flask 主应用架构
2. WHEN 配置系统时 THEN FoxTrends SHALL 使用 pydantic-settings 管理配置并支持 .env 文件
3. WHEN 管理依赖时 THEN FoxTrends SHALL 使用 UV 替代 pip 进行包管理
4. WHEN 分析 requirements.txt 时 THEN FoxTrends SHALL 确保所有依赖与 UV 兼容
5. WHEN 系统运行时 THEN FoxTrends SHALL 保持 BettaFish 的数据库连接配置（支持 PostgreSQL 和 MySQL）

### 需求 2: Agent 系统重构

**用户故事**: 作为产品经理，我希望将原有的舆情分析 Agent 重构为需求追踪 Agent，以便适应垂直社区需求分析场景。

#### 验收标准

1. WHEN 重构 InsightEngine 时 THEN FoxTrends SHALL 将其改造为 CommunityInsightAgent 用于社区历史数据分析
2. WHEN 重构 MediaEngine 时 THEN FoxTrends SHALL 将其改造为 ContentAnalysisAgent 用于社区内容多模态分析
3. WHEN Agent 协作时 THEN FoxTrends SHALL 保留 ForumEngine 的论坛协作机制
4. WHEN Agent 生成输出时 THEN FoxTrends SHALL 复用 BettaFish 的 SummaryNode 和 ReflectionNode 模式

### 需求 3: 垂直社区监控功能

**用户故事**: 作为社区运营者，我希望系统能够监控多个垂直社区的动态，以便及时发现用户需求和痛点。

#### 验收标准

1. WHEN 配置监控目标时 THEN NicheEngine SHALL 支持添加多个垂直社区数据源（Reddit、Discord、GitHub Issues、HackerNews 等）
2. WHEN 采集社区数据时 THEN NicheEngine SHALL 复用 MindSpider 的爬虫架构进行数据抓取
3. WHEN 存储社区数据时 THEN NicheEngine SHALL 将数据存储到与 BettaFish 兼容的数据库结构中
4. WHEN 识别需求信号时 THEN NicheEngine SHALL 提取用户痛点、功能请求、问题反馈等需求信号
5. WHEN 更新监控状态时 THEN NicheEngine SHALL 提供实时监控状态和数据采集进度

### 需求 4: Dashboard 前端开发

**用户故事**: 作为系统用户，我希望通过直观的 Dashboard 查看需求分析结果，以便快速了解社区动态。

#### 验收标准

1. WHEN 访问 Dashboard 时 THEN FoxTrends SHALL 提供基于 BettaFish 前端风格的统一界面
2. WHEN 查看社区监控时 THEN Dashboard SHALL 展示各垂直社区的实时监控状态和数据统计
3. WHEN 查看需求列表时 THEN Dashboard SHALL 展示按热度排序的需求列表和详细信息
4. WHEN 导出报告时 THEN Dashboard SHALL 支持生成和下载需求分析报告（复用 ReportEngine）

### 需求 5: ForumEngine 讨论机制扩展

**用户故事**: 作为系统架构师，我希望扩展 ForumEngine 以支持需求方向的多 Agent 讨论，以便生成高质量的需求分析报告。

#### 验收标准

1. WHEN Agent 发表观点时 THEN ForumEngine SHALL 记录各 Agent 对需求方向的分析和建议
2. WHEN 主持人总结时 THEN ForumEngine SHALL 使用 LLM 主持人整合各 Agent 的观点
3. WHEN 识别分歧时 THEN ForumEngine SHALL 标记 Agent 间的观点分歧并引导深入讨论
4. WHEN 生成共识时 THEN ForumEngine SHALL 提取 Agent 间的共识作为需求分析结论
5. WHEN 输出讨论记录时 THEN ForumEngine SHALL 将讨论过程记录到 forum.log 供后续分析

### 需求 6: 配置管理和部署

**用户故事**: 作为开发者，我希望系统配置管理简单清晰，以便快速部署和调试。

#### 验收标准

1. WHEN 初始化配置时 THEN FoxTrends SHALL 提供 .env.example 模板文件
2. WHEN 配置 LLM 时 THEN FoxTrends SHALL 支持为不同 Agent 配置不同的 LLM 模型
3. WHEN 配置数据库时 THEN FoxTrends SHALL 继承 BettaFish 的数据库配置方式
4. WHEN 使用 UV 安装依赖时 THEN FoxTrends SHALL 提供 pyproject.toml 和 uv.lock 文件
5. WHEN 部署系统时 THEN FoxTrends SHALL 支持 Docker 和源码两种部署方式

### 需求 7: 数据模型设计

**用户故事**: 作为数据工程师，我希望设计适合需求追踪的数据模型，以便高效存储和查询社区需求数据。

#### 验收标准

1. WHEN 设计数据表时 THEN FoxTrends SHALL 创建 communities 表存储垂直社区信息
2. WHEN 存储需求数据时 THEN FoxTrends SHALL 创建 demand_signals 表存储识别的需求信号
3. WHEN 关联数据时 THEN FoxTrends SHALL 建立表间外键关系确保数据完整性
4. WHEN 迁移数据时 THEN FoxTrends SHALL 提供数据库初始化和迁移脚本

### 需求 8: 测试和质量保证

**用户故事**: 作为质量工程师，我希望系统具有完善的测试覆盖，以便确保功能正确性和稳定性。

#### 验收标准

1. WHEN 测试 Agent 功能时 THEN FoxTrends SHALL 为每个 Agent 提供单元测试
2. WHEN 测试集成功能时 THEN FoxTrends SHALL 提供 ForumEngine 协作机制的集成测试
3. WHEN 测试数据采集时 THEN FoxTrends SHALL 提供 NicheEngine 爬虫功能的测试
4. WHEN 测试 API 接口时 THEN FoxTrends SHALL 提供 Flask API 端点的测试
5. WHEN 运行测试时 THEN FoxTrends SHALL 使用 pytest 作为测试框架

### 需求 9: 文档和示例

**用户故事**: 作为新用户，我希望有清晰的文档和示例，以便快速上手使用 FoxTrends。

#### 验收标准

1. WHEN 查看项目文档时 THEN FoxTrends SHALL 提供 README.md 说明系统功能和使用方法
2. WHEN 学习配置时 THEN FoxTrends SHALL 提供配置指南说明各配置项的作用
3. WHEN 学习开发时 THEN FoxTrends SHALL 提供开发文档说明代码结构和扩展方法
4. WHEN 查看示例时 THEN FoxTrends SHALL 提供示例配置和运行案例
5. WHEN 遇到问题时 THEN FoxTrends SHALL 提供常见问题解答和故障排查指南

## 变更记录

### 2025-11-22
- 移除需求 4（需求趋势分析）及 TrendEngine 相关内容
- 移除 TrendDiscoveryAgent（原需求 2.3）
- 简化 Dashboard 需求，移除趋势图表相关验收标准
- 更新需求编号：原需求 5-10 重新编号为需求 4-9
