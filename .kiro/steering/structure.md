# Project Structure

## Repository Organization

This is a **monorepo** containing two main projects:

```
/                           # BettaFish (root project)
├── FoxTrends/             # FoxTrends subproject (independent)
├── MindSpider/            # Crawler system (shared)
└── [other components]     # BettaFish components
```

## BettaFish Structure (Root)

### Agent Engines
- **QueryEngine/**: Domestic/international news search agent
- **MediaEngine/**: Multimodal content analysis agent
- **InsightEngine/**: Private database mining agent
- **ReportEngine/**: Multi-round report generation agent

Each agent follows this pattern:
```
AgentEngine/
├── agent.py              # Main agent logic
├── llms/                 # LLM interface wrappers
├── nodes/                # Processing nodes (search, summary, formatting)
├── tools/                # Agent-specific tools
├── state/                # State management
├── prompts/              # Prompt templates
└── utils/                # Utility functions
```

### Core Systems
- **ForumEngine/**: Agent collaboration "forum" mechanism
  - `monitor.py`: Log monitoring and forum management
  - `llm_host.py`: Forum moderator LLM module
- **MindSpider/**: Web crawler system for Chinese social platforms
  - `BroadTopicExtraction/`: Topic extraction from news
  - `DeepSentimentCrawling/`: Deep sentiment crawling with MediaCrawler
  - `schema/`: Database schema and initialization

### Supporting Components
- **SentimentAnalysisModel/**: Collection of sentiment analysis models
  - Fine-tuned BERT/GPT-2 models
  - Multilingual sentiment analysis
  - Traditional ML methods (SVM, XGBoost)
- **SingleEngineApp/**: Standalone Streamlit apps for each agent
- **templates/**: Flask HTML templates
- **static/**: Static assets (images, CSS)
- **utils/**: Shared utilities (forum_reader, retry_helper)
- **logs/**: Runtime logs (created at runtime)
- **final_reports/**: Generated HTML reports

### Configuration Files
- `app.py`: Flask main application entry
- `config.py`: Global configuration
- `.env`: Environment variables (not in repo)
- `requirements.txt`: Python dependencies
- `docker-compose.yml`: Docker deployment

## FoxTrends Structure (Subproject)

Located in `/FoxTrends/` directory with independent structure:

### Agent Engines (Adapted from BettaFish)
- **CommunityInsightAgent/**: Community historical data analysis (from InsightEngine)
- **ContentAnalysisAgent/**: Community content multimodal analysis (from MediaEngine)
- **TrendDiscoveryAgent/**: Demand trend discovery (from QueryEngine)

### FoxTrends-Specific Components
- **NicheEngine/**: Community monitoring engine
  - `engine.py`: Main monitoring logic
  - `models.py`: Data models for communities and demands
- **TrendEngine/**: Trend analysis engine (to be implemented)
- **Dashboard/**: Web dashboard UI (to be implemented)
- **database/**: Database management
  - `db_manager.py`: Database operations
  - `init_database.py`: Schema initialization

### Shared Components (Inherited)
- **ForumEngine/**: Reused from BettaFish
- **ReportEngine/**: Reused from BettaFish

### Configuration Files
- `app.py`: FoxTrends Flask application
- `config.py`: Pydantic Settings-based configuration
- `pyproject.toml`: UV package manager configuration
- `uv.lock`: Dependency lock file
- `.env`: Environment variables (not in repo)
- `tests/`: Property-based tests with pytest and hypothesis

## Key Architectural Patterns

### Multi-Agent Collaboration
1. User submits query via Flask web interface
2. Three agents start in parallel with specialized tools
3. Agents perform initial analysis and develop strategies
4. **Forum Loop**: Agents engage in iterative discussion
   - ForumEngine monitors agent communications
   - LLM moderator generates summaries and guidance
   - Agents adjust research based on forum insights
5. ReportEngine collects results and generates final report

### Configuration Management
- **BettaFish**: Manual config.py with environment variable fallbacks
- **FoxTrends**: Pydantic Settings with automatic .env loading and validation
- Both support runtime config updates via web interface

### Logging and Monitoring
- Structured logging with loguru
- Real-time log streaming via SocketIO
- Forum discussions logged to `logs/forum.log`
- Agent outputs logged to separate files

### Database Access
- SQLAlchemy ORM for database operations
- Async support with asyncpg/aiomysql
- Connection pooling for performance
- Schema migrations via init scripts

## Development Conventions

- **Python Style**: Follow PEP 8, use type hints where beneficial
- **Async**: Use async/await for I/O-bound operations
- **Error Handling**: Comprehensive try-except with logging
- **Testing**: Property-based testing with hypothesis (FoxTrends)
- **Modularity**: Each agent is self-contained with clear interfaces
- **Configuration**: All secrets in .env, never commit credentials
