"""
NicheEngine 数据模型
定义社区和需求信号的数据结构
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Community:
    """社区数据模型"""
    id: Optional[int] = None
    name: str = ""
    source_type: str = ""  # reddit, github, hackernews
    source_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: str = "active"  # active, paused, archived
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class DemandSignal:
    """需求信号数据模型"""
    id: Optional[int] = None
    community_id: Optional[int] = None
    signal_type: str = ""  # pain_point, feature_request, bug_report
    title: str = ""
    content: Optional[str] = None
    source_url: Optional[str] = None
    author: Optional[str] = None
    sentiment_score: Optional[float] = None  # -1.0 to 1.0
    hotness_score: Optional[float] = None  # 0.0 to 100.0
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    extracted_at: Optional[datetime] = None
