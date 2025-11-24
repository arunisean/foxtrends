#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告生成器

负责生成需求分析报告，包括单个需求报告和时间范围报告
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.safe_logger import safe_log_info, safe_log_error


class ReportGenerator:
    """
    报告生成器
    
    职责:
    - 生成单个需求的详细报告
    - 生成时间范围内的综合报告
    - 创建HTML格式的报告
    - 持久化报告到数据库
    """
    
    def __init__(self, db_manager=None):
        """
        初始化报告生成器
        
        Args:
            db_manager: 数据库管理器实例
        """
        if db_manager is None:
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager()
        
        self.db_manager = db_manager
        safe_log_info("ReportGenerator 初始化完成")
    
    def generate_single_demand_report(self, demand_id: int) -> Tuple[int, str]:
        """
        生成单个需求的详细报告
        
        Args:
            demand_id: 需求信号ID
            
        Returns:
            (report_id, report_path) 报告ID和文件路径
        """
        safe_log_info(f"开始生成需求报告: {demand_id}")
        
        try:
            # 1. 收集需求数据
            demand_data = self._gather_demand_data(demand_id)
            
            if not demand_data:
                raise ValueError(f"需求 {demand_id} 不存在")
            
            # 2. 收集Agent讨论
            discussions = self._gather_discussions(demand_id)
            
            # 3. 收集相关信号
            related_signals = self._gather_related_signals(demand_id, demand_data)
            
            # 4. 生成HTML报告
            html_content = self._render_single_demand_report(
                demand_data, 
                discussions, 
                related_signals
            )
            
            # 5. 保存报告到数据库
            report_id = self._save_report(
                title=f"需求分析报告 - {demand_data['title']}",
                report_type='single_demand',
                html_content=html_content,
                demand_signals=[demand_id],
                communities=[demand_data['community_id']]
            )
            
            # 6. 保存HTML文件
            report_path = self._save_html_file(report_id, html_content)
            
            safe_log_info(f"需求报告生成完成: {report_id}")
            return report_id, report_path
            
        except Exception as e:
            safe_log_error(f"生成需求报告失败: {e}")
            raise
    
    def generate_time_range_report(
        self, 
        start_date: datetime, 
        end_date: datetime,
        community_ids: Optional[List[int]] = None
    ) -> Tuple[int, str]:
        """
        生成时间范围内的综合报告
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            community_ids: 社区ID列表（可选，None表示所有社区）
            
        Returns:
            (report_id, report_path) 报告ID和文件路径
        """
        safe_log_info(f"开始生成时间范围报告: {start_date} 到 {end_date}")
        
        try:
            # 1. 收集时间范围内的需求信号
            signals = self._gather_signals_in_range(start_date, end_date, community_ids)
            
            if not signals:
                raise ValueError("指定时间范围内没有需求信号")
            
            # 2. 计算趋势统计
            trend_stats = self._calculate_trend_statistics(signals, start_date, end_date)
            
            # 3. 识别Top需求
            top_items = self._identify_top_items(signals)
            
            # 4. 社区级别分析
            community_breakdown = self._analyze_by_community(signals)
            
            # 5. 收集Agent洞察
            agent_insights = self._gather_agent_insights(signals)
            
            # 6. 生成HTML报告
            html_content = self._render_time_range_report(
                start_date,
                end_date,
                signals,
                trend_stats,
                top_items,
                community_breakdown,
                agent_insights
            )
            
            # 7. 保存报告到数据库
            report_id = self._save_report(
                title=f"需求趋势报告 ({start_date.date()} - {end_date.date()})",
                report_type='time_range',
                html_content=html_content,
                demand_signals=[s['id'] for s in signals],
                communities=community_ids or list(set(s['community_id'] for s in signals))
            )
            
            # 8. 保存HTML文件
            report_path = self._save_html_file(report_id, html_content)
            
            safe_log_info(f"时间范围报告生成完成: {report_id}")
            return report_id, report_path
            
        except Exception as e:
            safe_log_error(f"生成时间范围报告失败: {e}")
            raise
    
    def _gather_demand_data(self, demand_id: int) -> Optional[Dict[str, Any]]:
        """收集需求数据"""
        from sqlalchemy import text
        
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT 
                            ds.id, ds.title, ds.content, ds.signal_type,
                            ds.sentiment_score, ds.hotness_score,
                            ds.source_url, ds.author,
                            ds.discussion_count, ds.participant_count,
                            ds.created_at, ds.community_id,
                            c.name as community_name, c.source_type
                        FROM demand_signals ds
                        LEFT JOIN communities c ON ds.community_id = c.id
                        WHERE ds.id = :demand_id
                    """),
                    {'demand_id': demand_id}
                )
                
                row = result.fetchone()
                if not row:
                    return None
                
                return {
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'signal_type': row[3],
                    'sentiment_score': row[4],
                    'hotness_score': row[5],
                    'source_url': row[6],
                    'author': row[7],
                    'discussion_count': row[8],
                    'participant_count': row[9],
                    'created_at': row[10],
                    'community_id': row[11],
                    'community_name': row[12],
                    'source_type': row[13]
                }
        except Exception as e:
            safe_log_error(f"收集需求数据失败: {e}")
            return None
    
    def _gather_discussions(self, demand_id: int) -> List[Dict[str, Any]]:
        """收集Agent讨论记录"""
        from sqlalchemy import text
        
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT agent_name, content, message_type, created_at
                        FROM agent_discussions
                        WHERE demand_id = :demand_id
                        ORDER BY created_at ASC
                    """),
                    {'demand_id': demand_id}
                )
                
                discussions = []
                for row in result:
                    discussions.append({
                        'agent_name': row[0],
                        'content': row[1],
                        'message_type': row[2],
                        'created_at': row[3]
                    })
                
                return discussions
        except Exception as e:
            safe_log_error(f"收集讨论记录失败: {e}")
            return []
    
    def _gather_related_signals(self, demand_id: int, demand_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """收集相关需求信号"""
        from sqlalchemy import text
        
        try:
            # 简单实现：同一社区、同一类型的其他信号
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT id, title, hotness_score, created_at
                        FROM demand_signals
                        WHERE community_id = :community_id
                          AND signal_type = :signal_type
                          AND id != :demand_id
                        ORDER BY hotness_score DESC
                        LIMIT 5
                    """),
                    {
                        'community_id': demand_data['community_id'],
                        'signal_type': demand_data['signal_type'],
                        'demand_id': demand_id
                    }
                )
                
                related = []
                for row in result:
                    related.append({
                        'id': row[0],
                        'title': row[1],
                        'hotness_score': row[2],
                        'created_at': row[3]
                    })
                
                return related
        except Exception as e:
            safe_log_error(f"收集相关信号失败: {e}")
            return []
    
    def _gather_signals_in_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        community_ids: Optional[List[int]]
    ) -> List[Dict[str, Any]]:
        """收集时间范围内的需求信号"""
        from sqlalchemy import text
        
        try:
            query = """
                SELECT 
                    ds.id, ds.title, ds.signal_type,
                    ds.sentiment_score, ds.hotness_score,
                    ds.discussion_count, ds.created_at,
                    ds.community_id, c.name as community_name
                FROM demand_signals ds
                LEFT JOIN communities c ON ds.community_id = c.id
                WHERE ds.created_at >= :start_date 
                  AND ds.created_at <= :end_date
            """
            
            params = {'start_date': start_date, 'end_date': end_date}
            
            if community_ids:
                placeholders = ','.join([f':cid{i}' for i in range(len(community_ids))])
                query += f" AND ds.community_id IN ({placeholders})"
                for i, cid in enumerate(community_ids):
                    params[f'cid{i}'] = cid
            
            query += " ORDER BY ds.created_at DESC"
            
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text(query), params)
                
                signals = []
                for row in result:
                    # Convert created_at to datetime if it's a string (SQLite returns strings)
                    created_at = row[6]
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            # If parsing fails, try alternative format
                            try:
                                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                            except ValueError:
                                try:
                                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    # If all parsing fails, use current time as fallback
                                    created_at = datetime.now()
                    
                    signals.append({
                        'id': row[0],
                        'title': row[1],
                        'signal_type': row[2],
                        'sentiment_score': row[3],
                        'hotness_score': row[4],
                        'discussion_count': row[5],
                        'created_at': created_at,
                        'community_id': row[7],
                        'community_name': row[8]
                    })
                
                return signals
        except Exception as e:
            safe_log_error(f"收集时间范围信号失败: {e}")
            return []
    
    def _calculate_trend_statistics(
        self, 
        signals: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """计算趋势统计"""
        if not signals:
            return {}
        
        total_count = len(signals)
        avg_hotness = sum(s['hotness_score'] or 0 for s in signals) / total_count
        avg_sentiment = sum(s['sentiment_score'] or 0 for s in signals) / total_count
        
        # 计算增长率（简化版：对比前后两半时间段）
        mid_date = start_date + (end_date - start_date) / 2
        first_half = [s for s in signals if s['created_at'] < mid_date]
        second_half = [s for s in signals if s['created_at'] >= mid_date]
        
        growth_rate = 0.0
        if len(first_half) > 0:
            growth_rate = ((len(second_half) - len(first_half)) / len(first_half)) * 100
        
        return {
            'total_count': total_count,
            'avg_hotness': round(avg_hotness, 2),
            'avg_sentiment': round(avg_sentiment, 2),
            'growth_rate': round(growth_rate, 1),
            'first_half_count': len(first_half),
            'second_half_count': len(second_half)
        }
    
    def _identify_top_items(self, signals: List[Dict[str, Any]]) -> Dict[str, List]:
        """识别Top需求"""
        # 按热度排序
        sorted_by_hotness = sorted(signals, key=lambda x: x['hotness_score'] or 0, reverse=True)
        
        # 按类型分组
        pain_points = [s for s in sorted_by_hotness if s['signal_type'] == 'pain_point'][:5]
        feature_requests = [s for s in sorted_by_hotness if s['signal_type'] == 'feature_request'][:5]
        bug_reports = [s for s in sorted_by_hotness if s['signal_type'] == 'bug_report'][:5]
        
        return {
            'top_pain_points': pain_points,
            'top_feature_requests': feature_requests,
            'top_bug_reports': bug_reports,
            'top_overall': sorted_by_hotness[:10]
        }
    
    def _analyze_by_community(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """按社区分析"""
        from collections import defaultdict
        
        community_stats = defaultdict(lambda: {
            'count': 0,
            'avg_hotness': 0,
            'signal_types': defaultdict(int)
        })
        
        for signal in signals:
            cid = signal['community_id']
            cname = signal['community_name']
            
            community_stats[cname]['count'] += 1
            community_stats[cname]['avg_hotness'] += signal['hotness_score'] or 0
            community_stats[cname]['signal_types'][signal['signal_type']] += 1
        
        # 计算平均值
        for cname in community_stats:
            count = community_stats[cname]['count']
            if count > 0:
                community_stats[cname]['avg_hotness'] /= count
                community_stats[cname]['avg_hotness'] = round(community_stats[cname]['avg_hotness'], 2)
        
        return dict(community_stats)
    
    def _gather_agent_insights(self, signals: List[Dict[str, Any]]) -> List[str]:
        """收集Agent洞察（从讨论中提取）"""
        # 简化实现：返回通用洞察
        insights = [
            f"分析了 {len(signals)} 个需求信号",
            "建议优先关注高热度的痛点需求",
            "建议定期跟踪需求演变趋势"
        ]
        return insights
    
    def _render_single_demand_report(
        self,
        demand_data: Dict[str, Any],
        discussions: List[Dict[str, Any]],
        related_signals: List[Dict[str, Any]]
    ) -> str:
        """渲染单个需求报告HTML"""
        # 简化的HTML模板
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>需求分析报告 - {demand_data['title']}</title>
    <style>
        body {{ font-family: 'Arial', sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #667eea; margin-top: 30px; }}
        .meta {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .meta-item {{ margin: 8px 0; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
        .badge-pain {{ background: #fee; color: #c33; }}
        .badge-feature {{ background: #efe; color: #3c3; }}
        .badge-bug {{ background: #ffe; color: #cc3; }}
        .discussion {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; border-radius: 4px; }}
        .agent-name {{ font-weight: bold; color: #667eea; }}
        .related-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .score {{ font-weight: bold; color: #ff6b6b; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 需求分析报告</h1>
        
        <div class="meta">
            <div class="meta-item"><strong>需求标题:</strong> {demand_data['title']}</div>
            <div class="meta-item"><strong>需求类型:</strong> <span class="badge badge-{demand_data['signal_type']}">{demand_data['signal_type']}</span></div>
            <div class="meta-item"><strong>来源社区:</strong> {demand_data['community_name']} ({demand_data['source_type']})</div>
            <div class="meta-item"><strong>热度分数:</strong> <span class="score">{demand_data['hotness_score']:.1f}</span></div>
            <div class="meta-item"><strong>情感分数:</strong> {demand_data['sentiment_score']:.2f}</div>
            <div class="meta-item"><strong>讨论数:</strong> {demand_data['discussion_count']}</div>
            <div class="meta-item"><strong>创建时间:</strong> {demand_data['created_at']}</div>
        </div>
        
        <h2>📝 需求内容</h2>
        <p>{demand_data['content'][:500]}...</p>
        
        <h2>🤖 Agent 分析讨论</h2>
        {''.join([f'<div class="discussion"><span class="agent-name">{d["agent_name"]}:</span> {d["content"][:200]}...</div>' for d in discussions]) if discussions else '<p>暂无讨论记录</p>'}
        
        <h2>🔗 相关需求</h2>
        {''.join([f'<div class="related-item"><strong>{r["title"]}</strong> (热度: {r["hotness_score"]:.1f})</div>' for r in related_signals]) if related_signals else '<p>暂无相关需求</p>'}
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999;">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>FoxTrends - 垂直社区需求追踪系统</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _render_time_range_report(
        self,
        start_date: datetime,
        end_date: datetime,
        signals: List[Dict[str, Any]],
        trend_stats: Dict[str, Any],
        top_items: Dict[str, List],
        community_breakdown: Dict[str, Any],
        agent_insights: List[str]
    ) -> str:
        """渲染时间范围报告HTML"""
        # 简化的HTML模板
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>需求趋势报告 ({start_date.date()} - {end_date.date()})</title>
    <style>
        body {{ font-family: 'Arial', sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #667eea; margin-top: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; margin-top: 8px; }}
        .top-item {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .community-stat {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .insight {{ background: #e7f3ff; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 需求趋势报告</h1>
        <p><strong>时间范围:</strong> {start_date.date()} 至 {end_date.date()}</p>
        
        <h2>📊 总体统计</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{trend_stats.get('total_count', 0)}</div>
                <div class="stat-label">总需求数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{trend_stats.get('avg_hotness', 0)}</div>
                <div class="stat-label">平均热度</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{trend_stats.get('growth_rate', 0)}%</div>
                <div class="stat-label">增长率</div>
            </div>
        </div>
        
        <h2>🔥 Top 需求</h2>
        <h3>痛点需求</h3>
        {''.join([f'<div class="top-item"><strong>{item["title"]}</strong> (热度: {item["hotness_score"]:.1f})</div>' for item in top_items.get('top_pain_points', [])]) if top_items.get('top_pain_points') else '<p>暂无数据</p>'}
        
        <h3>功能请求</h3>
        {''.join([f'<div class="top-item"><strong>{item["title"]}</strong> (热度: {item["hotness_score"]:.1f})</div>' for item in top_items.get('top_feature_requests', [])]) if top_items.get('top_feature_requests') else '<p>暂无数据</p>'}
        
        <h2>🏘️ 社区分析</h2>
        {''.join([f'<div class="community-stat"><strong>{cname}</strong>: {stats["count"]} 个需求, 平均热度 {stats["avg_hotness"]}</div>' for cname, stats in community_breakdown.items()])}
        
        <h2>💡 Agent 洞察</h2>
        {''.join([f'<div class="insight">{insight}</div>' for insight in agent_insights])}
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999;">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>FoxTrends - 垂直社区需求追踪系统</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _save_report(
        self,
        title: str,
        report_type: str,
        html_content: str,
        demand_signals: List[int],
        communities: List[int]
    ) -> int:
        """保存报告到数据库"""
        from sqlalchemy import text
        import json
        
        try:
            with self.db_manager.engine.begin() as conn:
                result = conn.execute(
                    text("""
                        INSERT INTO demand_reports 
                        (title, report_type, html_content, demand_signals, communities, generated_by)
                        VALUES 
                        (:title, :report_type, :html_content, :demand_signals, :communities, :generated_by)
                    """),
                    {
                        'title': title,
                        'report_type': report_type,
                        'html_content': html_content,
                        'demand_signals': json.dumps(demand_signals),
                        'communities': json.dumps(communities),
                        'generated_by': 'ReportGenerator'
                    }
                )
                
                report_id = result.lastrowid
                safe_log_info(f"报告已保存到数据库: {report_id}")
                return report_id
        except Exception as e:
            safe_log_error(f"保存报告失败: {e}")
            raise
    
    def _save_html_file(self, report_id: int, html_content: str) -> str:
        """保存HTML文件"""
        try:
            # 确保目录存在
            reports_dir = Path('final_reports')
            reports_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'report_{report_id}_{timestamp}.html'
            filepath = reports_dir / filename
            
            # 写入文件
            filepath.write_text(html_content, encoding='utf-8')
            
            safe_log_info(f"报告HTML已保存: {filepath}")
            return str(filepath)
        except Exception as e:
            safe_log_error(f"保存HTML文件失败: {e}")
            raise
