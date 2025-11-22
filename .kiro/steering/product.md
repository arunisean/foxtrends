# Product Overview

## BettaFish (Root Project)
Multi-agent public opinion analysis system that monitors 30+ social media platforms (Weibo, Xiaohongshu, TikTok, Kuaishou, etc.) to analyze sentiment, trends, and public discourse. Users interact conversationally to request analysis, and the system generates comprehensive HTML reports.

**Key Features:**
- AI-driven 24/7 monitoring across domestic and international social platforms
- Multi-agent collaboration via "Forum" mechanism for collective intelligence
- Multimodal content analysis (text, images, short videos)
- Sentiment analysis using fine-tuned models and statistical methods
- Automated report generation with customizable templates

## FoxTrends (Subproject)
Vertical community demand tracking system built on BettaFish architecture. Transforms sentiment analysis capabilities into demand discovery and analysis for niche communities (Reddit, GitHub Issues, HackerNews).

**Key Features:**
- Multi-community monitoring and demand signal extraction
- Trend analysis with time-series data and hotness scoring
- Agent collaboration for demand insights
- Real-time dashboard for demand visualization
- Converts public opinion analysis into product/market intelligence

**Relationship:** FoxTrends reuses BettaFish's core architecture (ForumEngine, ReportEngine, config system) but adapts agents for demand tracking scenarios. Both projects run independently.
