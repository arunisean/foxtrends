#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent协调器

负责协调三个Agent对需求信号进行分析，并通过ForumEngine进行讨论
"""

import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from CommunityInsightAgent.agent import CommunityInsightAgent
from ContentAnalysisAgent.agent import ContentAnalysisAgent
from TrendDiscoveryAgent.agent import TrendDiscoveryAgent
from utils.safe_logger import safe_log_info, safe_log_error


class AgentOrchestrator:
    """
    Agent协调器
    
    职责:
    - 协调三个Agent对需求信号进行分析
    - 通过ForumEngine组织Agent讨论
    - 存储讨论记录到数据库
    - 生成共识总结
    """
    
    def __init__(self, db_manager=None):
        """
        初始化Agent协调器
        
        Args:
            db_manager: 数据库管理器实例
        """
        if db_manager is None:
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager()
        
        self.db_manager = db_manager
        
        # 初始化三个Agent
        try:
            self.community_insight_agent = CommunityInsightAgent()
            self.content_analysis_agent = ContentAnalysisAgent()
            self.trend_discovery_agent = TrendDiscoveryAgent()
            safe_log_info("AgentOrchestrator: 三个Agent初始化成功")
        except Exception as e:
            safe_log_error(f"AgentOrchestrator: Agent初始化失败: {e}")
            raise
        
        # ForumEngine集成（可选）
        self.forum_available = False
        try:
            from ForumEngine.monitor import get_monitor
            self.forum_monitor = get_monitor()
            self.forum_available = True
            safe_log_info("AgentOrchestrator: ForumEngine集成成功")
        except Exception as e:
            safe_log_error(f"AgentOrchestrator: ForumEngine集成失败: {e}")
    
    def analyze_signal(self, signal_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析需求信号
        
        调用三个Agent对信号进行分析
        
        Args:
            signal_id: 需求信号ID
            signal_data: 需求信号数据（包含title, content等）
            
        Returns:
            分析结果字典
        """
        safe_log_info(f"AgentOrchestrator: 开始分析信号 {signal_id}")
        
        try:
            # 构建查询内容
            query = self._build_query(signal_data)
            
            # 并行调用三个Agent
            results = {}
            
            # 1. CommunityInsightAgent - 社区历史数据分析
            try:
                safe_log_info(f"AgentOrchestrator: 调用 CommunityInsightAgent")
                results['community_insight'] = self.community_insight_agent.run(query, signal_data=signal_data)
            except Exception as e:
                safe_log_error(f"AgentOrchestrator: CommunityInsightAgent 失败: {e}")
                results['community_insight'] = {'success': False, 'error': str(e)}
            
            # 2. ContentAnalysisAgent - 内容分析
            try:
                safe_log_info(f"AgentOrchestrator: 调用 ContentAnalysisAgent")
                results['content_analysis'] = self.content_analysis_agent.run(query, signal_data=signal_data)
            except Exception as e:
                safe_log_error(f"AgentOrchestrator: ContentAnalysisAgent 失败: {e}")
                results['content_analysis'] = {'success': False, 'error': str(e)}
            
            # 3. TrendDiscoveryAgent - 趋势发现
            try:
                safe_log_info(f"AgentOrchestrator: 调用 TrendDiscoveryAgent")
                results['trend_discovery'] = self.trend_discovery_agent.run(query, signal_data=signal_data)
            except Exception as e:
                safe_log_error(f"AgentOrchestrator: TrendDiscoveryAgent 失败: {e}")
                results['trend_discovery'] = {'success': False, 'error': str(e)}
            
            safe_log_info(f"AgentOrchestrator: 信号 {signal_id} 分析完成")
            
            return {
                'success': True,
                'signal_id': signal_id,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            safe_log_error(f"AgentOrchestrator: 分析信号失败: {e}")
            return {
                'success': False,
                'signal_id': signal_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def initiate_forum_discussion(self, signal_id: int, analysis_results: Dict[str, Any]) -> str:
        """
        发起论坛讨论
        
        基于Agent分析结果，通过ForumEngine组织讨论
        
        Args:
            signal_id: 需求信号ID
            analysis_results: Agent分析结果
            
        Returns:
            讨论会话ID
        """
        session_id = str(uuid.uuid4())
        
        safe_log_info(f"AgentOrchestrator: 发起论坛讨论 (session: {session_id})")
        
        try:
            if not self.forum_available:
                safe_log_info("AgentOrchestrator: ForumEngine不可用，跳过论坛讨论")
                return session_id
            
            # 将Agent分析结果写入forum.log
            # ForumEngine会自动监控并生成主持人发言
            results = analysis_results.get('results', {})
            
            for agent_name, result in results.items():
                if result.get('success'):
                    # 格式化Agent发言
                    speech = self._format_agent_speech(agent_name, result)
                    
                    # 写入forum.log
                    source_tag = self._get_agent_tag(agent_name)
                    self.forum_monitor.write_to_forum_log(speech, source_tag)
            
            safe_log_info(f"AgentOrchestrator: 论坛讨论已发起 (session: {session_id})")
            
        except Exception as e:
            safe_log_error(f"AgentOrchestrator: 发起论坛讨论失败: {e}")
        
        return session_id
    
    def store_discussion(self, session_id: str, demand_id: int):
        """
        存储讨论记录到数据库
        
        Args:
            session_id: 讨论会话ID
            demand_id: 需求信号ID
        """
        safe_log_info(f"AgentOrchestrator: 存储讨论记录 (session: {session_id}, demand: {demand_id})")
        
        try:
            if not self.forum_available:
                safe_log_info("AgentOrchestrator: ForumEngine不可用，无法存储讨论记录")
                return
            
            # 获取forum.log内容
            forum_logs = self.forum_monitor.get_forum_log_content()
            
            if not forum_logs:
                safe_log_info("AgentOrchestrator: 没有论坛讨论记录")
                return
            
            # 解析并存储每条发言
            from sqlalchemy import text
            import json
            
            with self.db_manager.engine.begin() as conn:
                for log_line in forum_logs:
                    # 解析日志行
                    parsed = self._parse_forum_log_line(log_line)
                    
                    if parsed:
                        # 存储到agent_discussions表
                        conn.execute(
                            text("""
                                INSERT INTO agent_discussions 
                                (session_id, demand_id, agent_name, message_type, content, metadata)
                                VALUES 
                                (:session_id, :demand_id, :agent_name, :message_type, :content, :metadata)
                            """),
                            {
                                'session_id': session_id,
                                'demand_id': demand_id,
                                'agent_name': parsed['agent_name'],
                                'message_type': parsed['message_type'],
                                'content': parsed['content'],
                                'metadata': json.dumps(parsed.get('metadata', {}))
                            }
                        )
            
            safe_log_info(f"AgentOrchestrator: 讨论记录已存储 ({len(forum_logs)} 条)")
            
        except Exception as e:
            safe_log_error(f"AgentOrchestrator: 存储讨论记录失败: {e}")
    
    def get_discussion_summary(self, session_id: str) -> Optional[str]:
        """
        获取讨论共识总结
        
        Args:
            session_id: 讨论会话ID
            
        Returns:
            共识总结文本
        """
        safe_log_info(f"AgentOrchestrator: 获取讨论总结 (session: {session_id})")
        
        try:
            from sqlalchemy import text
            
            with self.db_manager.engine.connect() as conn:
                # 查询该会话的所有讨论记录
                result = conn.execute(
                    text("""
                        SELECT agent_name, content, created_at
                        FROM agent_discussions
                        WHERE session_id = :session_id
                        ORDER BY created_at ASC
                    """),
                    {'session_id': session_id}
                )
                
                discussions = result.fetchall()
                
                if not discussions:
                    safe_log_info("AgentOrchestrator: 没有找到讨论记录")
                    return None
                
                # 生成简单的总结
                summary_parts = []
                
                # 按Agent分组
                agent_contents = {}
                for agent_name, content, created_at in discussions:
                    if agent_name not in agent_contents:
                        agent_contents[agent_name] = []
                    agent_contents[agent_name].append(content)
                
                # 构建总结
                summary_parts.append("=== 需求分析讨论总结 ===\n")
                
                for agent_name, contents in agent_contents.items():
                    summary_parts.append(f"\n【{agent_name}】")
                    # 取最后一条发言作为该Agent的观点
                    summary_parts.append(contents[-1][:200] + "..." if len(contents[-1]) > 200 else contents[-1])
                
                summary = "\n".join(summary_parts)
                
                safe_log_info(f"AgentOrchestrator: 讨论总结已生成")
                return summary
                
        except Exception as e:
            safe_log_error(f"AgentOrchestrator: 获取讨论总结失败: {e}")
            return None
    
    def _build_query(self, signal_data: Dict[str, Any]) -> str:
        """构建查询内容"""
        title = signal_data.get('title', '')
        content = signal_data.get('content', '')
        signal_type = signal_data.get('signal_type', '')
        
        query = f"需求类型: {signal_type}\n"
        query += f"标题: {title}\n"
        if content:
            # 限制内容长度
            content_preview = content[:500] + "..." if len(content) > 500 else content
            query += f"内容: {content_preview}"
        
        return query
    
    def _format_agent_speech(self, agent_name: str, result: Dict[str, Any]) -> str:
        """格式化Agent发言"""
        analysis = result.get('analysis', '')
        
        # 根据不同Agent提取关键信息
        if agent_name == 'community_insight':
            patterns = result.get('patterns', [])
            trends = result.get('trends', [])
            speech = f"{analysis}\n\n需求模式: {', '.join(patterns)}\n趋势: {', '.join(trends)}"
        
        elif agent_name == 'content_analysis':
            pain_points = result.get('pain_points', [])
            features = result.get('feature_requests', [])
            speech = f"{analysis}\n\n痛点: {', '.join(pain_points)}\n功能请求: {', '.join(features)}"
        
        elif agent_name == 'trend_discovery':
            demands = result.get('current_demands', [])
            priority = result.get('priority_analysis', [])
            speech = f"{analysis}\n\n当前需求: {', '.join(demands)}\n优先级: {', '.join(priority)}"
        
        else:
            speech = analysis
        
        return speech
    
    def _get_agent_tag(self, agent_name: str) -> str:
        """获取Agent标签"""
        tag_map = {
            'community_insight': 'COMMUNITY_INSIGHT',
            'content_analysis': 'CONTENT_ANALYSIS',
            'trend_discovery': 'TREND_DISCOVERY'
        }
        return tag_map.get(agent_name, agent_name.upper())
    
    def _parse_forum_log_line(self, log_line: str) -> Optional[Dict[str, Any]]:
        """解析forum.log行"""
        import re
        
        # 格式: [HH:MM:SS] [AGENT_NAME] content
        match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s*\[(\w+)\]\s*(.+)', log_line)
        
        if not match:
            return None
        
        timestamp, agent_name, content = match.groups()
        
        # 确定消息类型
        if agent_name == 'SYSTEM':
            message_type = 'system'
        elif agent_name == 'HOST':
            message_type = 'host'
        else:
            message_type = 'agent'
        
        return {
            'agent_name': agent_name,
            'message_type': message_type,
            'content': content,
            'metadata': {
                'timestamp': timestamp
            }
        }
