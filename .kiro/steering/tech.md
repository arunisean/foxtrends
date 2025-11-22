# Technology Stack

## Core Technologies

### Backend
- **Python**: 3.9+ (BettaFish), 3.11+ (FoxTrends)
- **Web Framework**: Flask with SocketIO for real-time communication
- **UI**: Streamlit for individual agent interfaces
- **Database**: PostgreSQL (recommended) or MySQL with SQLAlchemy ORM
- **Async**: aiohttp, asyncio, asyncpg for concurrent operations

### Package Management
- **BettaFish**: pip/conda with requirements.txt
- **FoxTrends**: UV package manager with pyproject.toml (modern, faster)

### LLM Integration
- OpenAI-compatible API interface (supports any provider with OpenAI format)
- Configured via environment variables for each agent
- Providers: Moonshot (Kimi), DeepSeek, Gemini, custom endpoints

### Web Scraping
- Playwright for browser automation
- BeautifulSoup4, lxml, parsel for HTML parsing
- MediaCrawler integration for Chinese social platforms

### Data Processing
- pandas, numpy for data manipulation
- jieba for Chinese text segmentation
- regex for pattern matching

### Machine Learning (Optional)
- PyTorch (CPU/GPU) for sentiment analysis models
- transformers for BERT/GPT-2 fine-tuned models
- scikit-learn, xgboost for traditional ML methods

### Visualization
- Plotly for interactive charts
- matplotlib for static plots
- wordcloud for text visualization

## Common Commands

### BettaFish

```bash
# Environment setup (conda)
conda create -n bettafish python=3.11
conda activate bettafish
pip install -r requirements.txt

# Install browser drivers
playwright install chromium

# Run main application
python app.py

# Run individual agents
streamlit run SingleEngineApp/query_engine_streamlit_app.py --server.port 8503
streamlit run SingleEngineApp/media_engine_streamlit_app.py --server.port 8502
streamlit run SingleEngineApp/insight_engine_streamlit_app.py --server.port 8501

# Crawler operations
cd MindSpider
python main.py --setup
python main.py --broad-topic
python main.py --complete --date 2024-01-20
```

### FoxTrends

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Environment setup (UV)
cd FoxTrends
uv sync

# Initialize database
uv run python database/init_database.py

# Run application
uv run python app.py

# Run tests
uv run pytest
uv run pytest --cov=FoxTrends --cov-report=html

# Development tools
uv run black .
uv run flake8
```

## Configuration

Both projects use `.env` files for configuration:
- Copy `.env.example` to `.env`
- Configure database connection (PostgreSQL/MySQL)
- Set LLM API keys and endpoints for each agent
- Configure search APIs (Tavily, Bocha)
- Set crawler parameters and data source credentials

Configuration is managed via:
- **BettaFish**: `config.py` with manual parsing
- **FoxTrends**: Pydantic Settings with automatic validation

## Docker Deployment

```bash
# BettaFish
docker compose up -d

# Note: Mirror alternatives provided in docker-compose.yml comments for slow pulls
```
