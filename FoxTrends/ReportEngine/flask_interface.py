"""
ReportEngine Flask接口
提供报告生成的API端点
"""

from flask import Blueprint, render_template
from datetime import datetime
from pathlib import Path
import os

report_bp = Blueprint('report', __name__)

def initialize_report_engine():
    """初始化ReportEngine"""
    # 创建报告目录
    report_dir = Path('final_reports')
    report_dir.mkdir(exist_ok=True)
    return True

def generate_demand_analysis_report(demands, time_range='30天'):
    """生成需求分析报告"""
    from jinja2 import Environment, FileSystemLoader
    
    # 设置模板环境
    template_dir = Path(__file__).parent / 'templates'
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template('demand_analysis_report.html')
    
    # 计算统计数据
    total_demands = len(demands)
    avg_hotness = sum(d.get('hotness_score', 0) for d in demands) / total_demands if total_demands > 0 else 0
    high_priority = sum(1 for d in demands if d.get('hotness_score', 0) >= 70)
    communities = set(d.get('community', '') for d in demands)
    
    # 生成洞察
    insights = [
        {
            'title': '需求趋势',
            'content': f'在过去{time_range}内，共收集到 {total_demands} 个需求信号，平均热度为 {avg_hotness:.1f}。'
        },
        {
            'title': '高优先级需求',
            'content': f'其中 {high_priority} 个需求被标记为高优先级（热度 ≥ 70），需要重点关注。'
        },
        {
            'title': '社区分布',
            'content': f'需求来自 {len(communities)} 个不同的社区，显示出广泛的用户基础。'
        }
    ]
    
    # 准备需求数据
    signal_type_map = {
        'pain_point': '痛点',
        'feature_request': '功能请求',
        'bug_report': '问题反馈'
    }
    
    for demand in demands:
        demand['signal_type_text'] = signal_type_map.get(demand.get('signal_type', ''), demand.get('signal_type', ''))
    
    # 生成摘要
    summary = f'本报告分析了过去{time_range}内从 {len(communities)} 个社区收集的 {total_demands} 个需求信号。' \
              f'平均热度为 {avg_hotness:.1f}，其中 {high_priority} 个高优先级需求需要重点关注。'
    
    # 渲染模板
    html_content = template.render(
        report_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        time_range=time_range,
        summary=summary,
        total_demands=total_demands,
        avg_hotness=f'{avg_hotness:.1f}',
        high_priority=high_priority,
        communities_count=len(communities),
        insights=insights,
        demands=demands,
        agent_analysis=[]  # 可以后续添加 Agent 分析
    )
    
    # 保存报告
    report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    report_path = Path('final_reports') / f'{report_id}.html'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_id, str(report_path)

@report_bp.route('/generate', methods=['POST'])
def generate_report():
    """生成报告API"""
    return {"success": True, "message": "ReportEngine功能开发中"}
