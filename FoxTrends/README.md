# FoxTrends

**Multi-vertical Community Demand Tracking System**

FoxTrends 是基于 BettaFish 舆情分析系统深度改造的多垂直社区需求追踪平台。系统复用 BettaFish 的多 Agent 协作机制，将原有的舆情分析能力转化为垂直社区（niche communities）的需求发现和分析能力。

## 核心特性

- 🤖 **多 Agent 协作**: 继承 BettaFish 的 Agent 协作架构
- 🌐 **多社区监控**: 支持 Reddit、GitHub Issues、HackerNews 等多个社区数据源
- 📊 **趋势分析**: 时间序列分析、热度计算、趋势预测
- 💬 **ForumEngine**: Agent 讨论和观点整合机制
- 📈 **可视化 Dashboard**: 直观的需求分析和趋势展示
- 🔄 **实时更新**: SocketIO 实时数据推送

## 系统架构

FoxTrends 包含以下核心组件：

### Agent 层
- **CommunityInsightAgent**: 社区历史数据分析（改造自 InsightEngine）
- **ContentAnalysisAgent**: 社区内容多模态分析（改造自 MediaEngine）
- **TrendDiscoveryAgent**: 需求趋势发现（改造自 QueryEngine）

### 功能层
- **NicheEngine**: 社区监控引擎，负责数据采集和需求信号提取
- **TrendEngine**: 趋势分析引擎，负责热度计算和趋势预测
- **ForumEngine**: 论坛引擎，负责 Agent 协作和讨论管理
- **ReportEngine**: 报告生成引擎，负责生成需求分析报告

### 展示层
- **Dashboard**: Web 界面，提供可视化的需求分析和管理功能

## 快速开始

### 环境要求

- Python 3.11+
- UV 包管理工具
- SQLite（默认，无需额外安装）或 PostgreSQL/MySQL（可选）

### 一键启动（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd FoxTrends

# 一键启动（自动安装依赖、初始化数据库、启动服务）
./quick_start.sh
```

启动后访问：http://localhost:5000/

### 一键停止

```bash
# 停止所有 FoxTrends 进程
./quick_stop.sh
```

### 手动安装步骤

如果需要手动控制每个步骤：

1. 克隆项目
```bash
git clone <repository-url>
cd FoxTrends
```

2. 安装 UV（如果尚未安装）
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. 使用 UV 安装依赖
```bash
uv sync
```

4. 配置环境变量（可选）
```bash
cp .env.example .env
# 编辑 .env 文件，填入 LLM API 密钥等配置
# 数据库默认使用 SQLite，无需额外配置
```

5. 初始化数据库
```bash
uv run python database/init_database.py
```

6. 启动服务
```bash
uv run python app.py
```

7. 访问 Dashboard
```bash
# 浏览器打开
http://localhost:5000/
```

## 常用命令

### 启动和停止

```bash
# 启动服务
./quick_start.sh

# 停止服务
./quick_stop.sh
```

### 数据管理

```bash
# 清理测试数据
uv run python scripts/clean_test_data.py

# 验证无mock数据
uv run python scripts/verify_no_mock_data.py

# 初始化数据库
uv run python database/init_database.py
```

### 开发和测试

```bash
# 运行测试
uv run pytest

# 生成测试覆盖率报告
uv run pytest --cov=FoxTrends --cov-report=html

# 查看日志
tail -f logs/forum.log
```

## 配置说明

详细的配置说明请参考 `.env.example` 文件。主要配置项包括：

### 数据库配置
- **SQLite** (默认): 开箱即用，无需额外配置
  ```env
  DB_DIALECT=sqlite
  DB_NAME=foxtrends.db
  ```

- **PostgreSQL/MySQL** (可选): 适用于生产环境
  ```env
  DB_DIALECT=postgresql  # 或 mysql
  DB_HOST=localhost
  DB_PORT=5432
  DB_USER=foxtrends_user
  DB_PASSWORD=your_password
  DB_NAME=foxtrends
  ```

### 其他配置
- **LLM Agent 配置**: 为每个 Agent 配置独立的 LLM API
- **社区数据源**: Reddit、GitHub、HackerNews 等 API 配置
- **爬取策略**: 爬取间隔、深度、数量等参数

## 技术栈

- **后端**: Python 3.11+, Flask, SQLAlchemy
- **数据库**: SQLite (默认) / PostgreSQL / MySQL
- **LLM**: OpenAI API 兼容接口
- **爬虫**: Playwright, aiohttp, BeautifulSoup4
- **前端**: Jinja2, Plotly.js
- **包管理**: UV

## 开发指南

### 项目结构

```
FoxTrends/
├── config.py              # 配置管理
├── app.py                 # Flask 主应用
├── CommunityInsightAgent/ # 社区洞察 Agent
├── ContentAnalysisAgent/  # 内容分析 Agent
├── TrendDiscoveryAgent/   # 趋势发现 Agent
├── NicheEngine/           # 社区监控引擎
├── TrendEngine/           # 趋势分析引擎
├── ForumEngine/           # 论坛引擎
├── ReportEngine/          # 报告生成引擎
├── Dashboard/             # Web 界面
├── tests/                 # 测试文件
└── scripts/               # 工具脚本
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_config.py

# 生成覆盖率报告
uv run pytest --cov=FoxTrends --cov-report=html
```

## 许可证

MIT License

## 致谢

本项目基于 [BettaFish](https://github.com/your-repo/BettaFish) 改造，感谢原项目的贡献者。
