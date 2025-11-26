# ForumEngine 配置说明

## Forum 参与者配置

ForumEngine 的参与者（Agent）是通过**日志文件监控**自动识别的，不需要手动配置参与者列表。

### 工作原理

```
┌─────────────────────────────────────────────────────────────┐
│  ForumEngine Monitor (monitor.py)                            │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  监控的日志文件:                                         ││
│  │  - logs/community_insight.log                           ││
│  │  - logs/content_analysis.log                            ││
│  │  - logs/trend_discovery.log                             ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  当检测到 Agent 输出时:                                      │
│  1. 提取 Agent 的发言内容                                    │
│  2. 写入 logs/forum.log                                      │
│  3. 触发 Forum Host 生成主持人发言                           │
└─────────────────────────────────────────────────────────────┘
```

## 配置文件位置

### 1. 环境变量配置 (`.env`)

```env
# ======================= LLM Agent 配置 =======================

# CommunityInsight Agent（推荐 kimi-k2）
COMMUNITY_INSIGHT_API_KEY=your_api_key_here
COMMUNITY_INSIGHT_BASE_URL=https://api.moonshot.cn/v1
COMMUNITY_INSIGHT_MODEL_NAME=moonshot-v1-128k

# ContentAnalysis Agent（推荐 gemini-2.5-pro）
CONTENT_ANALYSIS_API_KEY=your_api_key_here
CONTENT_ANALYSIS_BASE_URL=https://generativelanguage.googleapis.com/v1beta
CONTENT_ANALYSIS_MODEL_NAME=gemini-2.0-flash-exp

# TrendDiscovery Agent（推荐 deepseek）
TREND_DISCOVERY_API_KEY=your_api_key_here
TREND_DISCOVERY_BASE_URL=https://api.deepseek.com/v1
TREND_DISCOVERY_MODEL_NAME=deepseek-chat

# Forum Host（推荐 qwen-plus）
FORUM_HOST_API_KEY=your_api_key_here
FORUM_HOST_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
FORUM_HOST_MODEL_NAME=qwen-plus
```

### 2. 代码配置 (`config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Community Insight Agent
    COMMUNITY_INSIGHT_API_KEY: str = ""
    COMMUNITY_INSIGHT_BASE_URL: str = "https://api.moonshot.cn/v1"
    COMMUNITY_INSIGHT_MODEL_NAME: str = "moonshot-v1-128k"
    
    # Content Analysis Agent
    CONTENT_ANALYSIS_API_KEY: str = ""
    CONTENT_ANALYSIS_BASE_URL: str = ""
    CONTENT_ANALYSIS_MODEL_NAME: str = "gemini-2.0-flash-exp"
    
    # Trend Discovery Agent
    TREND_DISCOVERY_API_KEY: str = ""
    TREND_DISCOVERY_BASE_URL: str = "https://api.deepseek.com/v1"
    TREND_DISCOVERY_MODEL_NAME: str = "deepseek-chat"
    
    # Forum Host
    FORUM_HOST_API_KEY: str = ""
    FORUM_HOST_BASE_URL: str = ""
    FORUM_HOST_MODEL_NAME: str = "qwen-plus"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## Agent 识别机制

### 1. 日志文件映射

ForumEngine 通过监控特定的日志文件来识别 Agent：

```python
# monitor.py 中的配置
self.monitored_logs = {
    'community_insight': self.log_dir / 'community_insight.log',
    'content_analysis': self.log_dir / 'content_analysis.log',
    'trend_discovery': self.log_dir / 'trend_discovery.log'
}
```

### 2. Agent 标签映射

当 Agent 发言时，会被标记为特定的标签：

```python
# agent_orchestrator.py 中的映射
def _get_agent_tag(self, agent_name: str) -> str:
    tag_map = {
        'community_insight': 'COMMUNITY_INSIGHT',
        'content_analysis': 'CONTENT_ANALYSIS',
        'trend_discovery': 'TREND_DISCOVERY'
    }
    return tag_map.get(agent_name, agent_name.upper())
```

### 3. Forum.log 格式

```
[10:30:15] [COMMUNITY_INSIGHT] 基于社区历史数据分析，这是一个持续性的性能问题...
[10:30:45] [CONTENT_ANALYSIS] 从内容分析来看，用户对响应速度的关注度很高...
[10:31:10] [TREND_DISCOVERY] 当前趋势显示，性能优化需求正在快速增长...
[10:31:30] [HOST] 综合各位Agent的分析，我们可以看到...
```

## 添加新的 Agent

如果要添加新的 Agent 参与 Forum 讨论，需要：

### 1. 创建 Agent 类

```python
# FoxTrends/NewAgent/agent.py
class NewAgent:
    def __init__(self):
        self.api_key = settings.NEW_AGENT_API_KEY
        self.base_url = settings.NEW_AGENT_BASE_URL
        self.model = settings.NEW_AGENT_MODEL_NAME
        # ...
    
    def run(self, query, signal_data=None):
        # Agent 逻辑
        pass
```

### 2. 添加环境变量

```env
# .env
NEW_AGENT_API_KEY=your_api_key
NEW_AGENT_BASE_URL=https://api.example.com/v1
NEW_AGENT_MODEL_NAME=model-name
```

### 3. 更新 ForumEngine 监控配置

```python
# monitor.py
self.monitored_logs = {
    'community_insight': self.log_dir / 'community_insight.log',
    'content_analysis': self.log_dir / 'content_analysis.log',
    'trend_discovery': self.log_dir / 'trend_discovery.log',
    'new_agent': self.log_dir / 'new_agent.log',  # 新增
}
```

### 4. 更新 AgentOrchestrator

```python
# agent_orchestrator.py
def __init__(self, db_manager=None):
    # ...
    self.new_agent = NewAgent()  # 新增
    
def analyze_signal(self, signal_id, signal_data):
    # ...
    # 阶段 4: NewAgent
    try:
        results['new_agent'] = self.new_agent.run(query, signal_data=enhanced_signal_data)
    except Exception as e:
        results['new_agent'] = {'success': False, 'error': str(e)}
```

### 5. 更新标签映射

```python
def _get_agent_tag(self, agent_name: str) -> str:
    tag_map = {
        'community_insight': 'COMMUNITY_INSIGHT',
        'content_analysis': 'CONTENT_ANALYSIS',
        'trend_discovery': 'TREND_DISCOVERY',
        'new_agent': 'NEW_AGENT',  # 新增
    }
    return tag_map.get(agent_name, agent_name.upper())
```

## Forum Host 配置

### 主持人触发机制

```python
# monitor.py
self.host_speech_threshold = 5  # 每5条Agent发言触发一次主持人发言
```

当累积了 5 条 Agent 发言后，ForumEngine 会自动调用 Forum Host 生成主持人发言。

### 主持人 Prompt

主持人的行为由 `llm_host.py` 中的 system prompt 定义：

```python
def _build_system_prompt(self) -> str:
    return """你是FoxTrends多垂直社区需求追踪系统的论坛主持人。你的职责是：

1. **需求梳理**：从各agent的发言中识别关键需求信号
2. **引导讨论**：根据各agent的发言，引导深入讨论
3. **纠正错误**：如果发现需求理解错误或逻辑矛盾，请明确指出
4. **整合观点**：综合不同agent的视角，形成更全面的需求认识
5. **趋势预测**：基于已有信息分析需求发展趋势
6. **推进分析**：提出新的分析角度或需要关注的问题
    
    ...
    """
```

### 自定义主持人行为

可以通过修改 `_build_system_prompt()` 和 `_build_user_prompt()` 来自定义主持人的行为：

```python
# llm_host.py
def _build_system_prompt(self) -> str:
    # 修改这里来改变主持人的角色定位和行为准则
    return """你的自定义 system prompt..."""

def _build_user_prompt(self, parsed_content: Dict[str, Any]) -> str:
    # 修改这里来改变主持人发言的结构和重点
    return """你的自定义 user prompt..."""
```

## 配置最佳实践

### 1. API Key 管理

```bash
# 使用环境变量（推荐）
export COMMUNITY_INSIGHT_API_KEY="sk-xxx"
export CONTENT_ANALYSIS_API_KEY="sk-yyy"
export TREND_DISCOVERY_API_KEY="sk-zzz"
export FORUM_HOST_API_KEY="sk-www"

# 或使用 .env 文件
cp .env.example .env
# 编辑 .env 文件填入 API Key
```

### 2. 模型选择建议

| Agent | 推荐模型 | 原因 |
|-------|---------|------|
| Community Insight | Moonshot (Kimi) | 长上下文，适合历史数据分析 |
| Content Analysis | Gemini 2.0 Flash | 多模态能力强，速度快 |
| Trend Discovery | DeepSeek | 推理能力强，成本低 |
| Forum Host | Qwen Plus | 中文理解好，总结能力强 |

### 3. 成本控制

```env
# 使用更便宜的模型
COMMUNITY_INSIGHT_MODEL_NAME=moonshot-v1-8k  # 而不是 128k
CONTENT_ANALYSIS_MODEL_NAME=gemini-1.5-flash  # 而不是 pro
TREND_DISCOVERY_MODEL_NAME=deepseek-chat  # 已经很便宜
FORUM_HOST_MODEL_NAME=qwen-turbo  # 而不是 plus
```

### 4. 超时和重试配置

```env
# Agent 执行配置
AGENT_TIMEOUT=60  # 单个 Agent 超时时间（秒）
AGENT_MAX_RETRIES=2  # 失败重试次数
PIPELINE_STAGE_DELAY=1  # 阶段之间的延迟（秒）
```

## 监控和调试

### 1. 查看 Forum 日志

```bash
# 实时查看 forum.log
tail -f logs/forum.log

# 查看最近的讨论
tail -n 50 logs/forum.log
```

### 2. 查看 Agent 日志

```bash
# 查看各个 Agent 的日志
tail -f logs/community_insight.log
tail -f logs/content_analysis.log
tail -f logs/trend_discovery.log
```

### 3. 调试 ForumEngine

```python
# 在代码中启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 或使用 loguru
from loguru import logger
logger.add("debug.log", level="DEBUG")
```

## 常见问题

### Q1: Agent 发言没有出现在 forum.log 中？

**可能原因**:
1. Agent 日志文件路径不正确
2. Agent 输出格式不符合监控模式
3. ForumEngine 监控未启动

**解决方案**:
```python
# 检查监控状态
from ForumEngine.monitor import get_monitor
monitor = get_monitor()
print(f"监控状态: {monitor.is_monitoring}")
print(f"监控文件: {monitor.monitored_logs}")
```

### Q2: Forum Host 不生成发言？

**可能原因**:
1. API Key 未配置或错误
2. Agent 发言数量未达到阈值（默认5条）
3. llm_host.py 导入失败

**解决方案**:
```python
# 测试 Forum Host
from ForumEngine.llm_host import generate_host_speech
test_logs = [
    "[10:30:00] [COMMUNITY_INSIGHT] 测试发言1",
    "[10:30:01] [CONTENT_ANALYSIS] 测试发言2",
    # ... 至少5条
]
speech = generate_host_speech(test_logs)
print(speech)
```

### Q3: 如何调整主持人发言频率？

```python
# monitor.py
self.host_speech_threshold = 3  # 改为每3条Agent发言触发一次
```

### Q4: 如何禁用 Forum Host？

```python
# monitor.py
HOST_AVAILABLE = False  # 设置为 False
```

或在 `.env` 中不配置 `FORUM_HOST_API_KEY`。

## 总结

ForumEngine 的配置非常灵活：

✅ **自动识别**: 通过日志文件自动识别参与的 Agent
✅ **易于扩展**: 添加新 Agent 只需几步配置
✅ **灵活配置**: 可以自定义主持人行为和触发机制
✅ **成本可控**: 可以选择不同价位的模型

关键配置点：
1. `.env` 文件中的 API Key 和模型配置
2. `monitor.py` 中的日志文件映射
3. `llm_host.py` 中的主持人 prompt
4. `agent_orchestrator.py` 中的 Agent 编排逻辑
