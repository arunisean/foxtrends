"""
FoxTrends Flask主应用 - 多垂直社区需求追踪系统
基于 BettaFish 架构改造，用于需求发现和分析
"""

import os
import sys
import subprocess
import time
import threading
from datetime import datetime
from queue import Queue
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import atexit
import requests
from loguru import logger
import importlib
from pathlib import Path

# 导入配置
sys.path.insert(0, str(Path(__file__).parent))
from config import settings, reload_settings

# 导入ReportEngine
try:
    from ReportEngine.flask_interface import report_bp, initialize_report_engine
    REPORT_ENGINE_AVAILABLE = True
except ImportError as e:
    logger.error(f"ReportEngine导入失败: {e}")
    REPORT_ENGINE_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FoxTrends-Niche-Community-Demand-Tracking-System'
socketio = SocketIO(app, cors_allowed_origins="*")

# 注册ReportEngine Blueprint
if REPORT_ENGINE_AVAILABLE:
    app.register_blueprint(report_bp, url_prefix='/api/report')
    logger.info("ReportEngine接口已注册")
else:
    logger.info("ReportEngine不可用，跳过接口注册")

# 设置UTF-8编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# 创建日志目录
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

# 配置键列表
CONFIG_KEYS = [
    'HOST',
    'PORT',
    'DB_DIALECT',
    'DB_HOST',
    'DB_PORT',
    'DB_USER',
    'DB_PASSWORD',
    'DB_NAME',
    'DB_CHARSET',
    # Agent配置
    'COMMUNITY_INSIGHT_AGENT_API_KEY',
    'COMMUNITY_INSIGHT_AGENT_BASE_URL',
    'COMMUNITY_INSIGHT_AGENT_MODEL_NAME',
    'CONTENT_ANALYSIS_AGENT_API_KEY',
    'CONTENT_ANALYSIS_AGENT_BASE_URL',
    'CONTENT_ANALYSIS_AGENT_MODEL_NAME',
    'TREND_DISCOVERY_AGENT_API_KEY',
    'TREND_DISCOVERY_AGENT_BASE_URL',
    'TREND_DISCOVERY_AGENT_MODEL_NAME',
    # ForumEngine配置
    'FORUM_HOST_API_KEY',
    'FORUM_HOST_BASE_URL',
    'FORUM_HOST_MODEL_NAME',
    # ReportEngine配置
    'REPORT_ENGINE_API_KEY',
    'REPORT_ENGINE_BASE_URL',
    'REPORT_ENGINE_MODEL_NAME',
    # 社区数据源配置
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT',
    'GITHUB_TOKEN',
    'HACKERNEWS_API_BASE_URL',
    # NicheEngine配置
    'NICHE_ENGINE_MAX_CONCURRENT_CRAWLS',
    'NICHE_ENGINE_CRAWL_INTERVAL',
    # TrendEngine配置
    'TREND_ENGINE_ANALYSIS_WINDOW_DAYS',
    'TREND_ENGINE_PREDICTION_HORIZON_DAYS'
]


def read_config_values():
    """返回当前配置值"""
    try:
        reload_settings()
        values = {}
        for key in CONFIG_KEYS:
            value = getattr(settings, key, None)
            if value is None:
                values[key] = ''
            else:
                values[key] = str(value)
        return values
    except Exception as exc:
        logger.exception(f"读取配置失败: {exc}")
        return {}


def write_config_values(updates):
    """持久化配置更新到.env文件"""
    from pathlib import Path
    
    project_root = Path(__file__).resolve().parent
    cwd_env = Path.cwd() / ".env"
    env_file_path = cwd_env if cwd_env.exists() else (project_root / ".env")
    
    env_lines = []
    env_key_indices = {}
    if env_file_path.exists():
        env_lines = env_file_path.read_text(encoding='utf-8').splitlines()
        for i, line in enumerate(env_lines):
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('#'):
                if '=' in line_stripped:
                    key = line_stripped.split('=')[0].strip()
                    env_key_indices[key] = i
    
    for key, raw_value in updates.items():
        if raw_value is None or raw_value == '':
            env_value = ''
        elif isinstance(raw_value, (int, float)):
            env_value = str(raw_value)
        elif isinstance(raw_value, bool):
            env_value = 'True' if raw_value else 'False'
        else:
            value_str = str(raw_value)
            if ' ' in value_str or '\n' in value_str or '#' in value_str:
                escaped = value_str.replace('\\', '\\\\').replace('"', '\\"')
                env_value = f'"{escaped}"'
            else:
                env_value = value_str
        
        if key in env_key_indices:
            env_lines[env_key_indices[key]] = f'{key}={env_value}'
        else:
            env_lines.append(f'{key}={env_value}')
    
    env_file_path.parent.mkdir(parents=True, exist_ok=True)
    env_file_path.write_text('\n'.join(env_lines) + '\n', encoding='utf-8')
    reload_settings()


# 系统状态管理
system_state_lock = threading.Lock()
system_state = {
    'started': False,
    'starting': False
}


def _set_system_state(*, started=None, starting=None):
    """安全更新系统状态"""
    with system_state_lock:
        if started is not None:
            system_state['started'] = started
        if starting is not None:
            system_state['starting'] = starting


def _get_system_state():
    """获取系统状态副本"""
    with system_state_lock:
        return system_state.copy()


def _prepare_system_start():
    """准备系统启动"""
    with system_state_lock:
        if system_state['started']:
            return False, '系统已启动'
        if system_state['starting']:
            return False, '系统正在启动'
        system_state['starting'] = True
        return True, None


# 初始化数据库
def initialize_database():
    """初始化FoxTrends数据库"""
    try:
        from database.init_database import init_database
        logger.info("开始初始化数据库...")
        if init_database():
            logger.info("数据库初始化成功")
            return True
        else:
            logger.error("数据库初始化失败")
            return False
    except Exception as e:
        logger.exception(f"数据库初始化异常: {e}")
        return False


# 初始化ForumEngine的forum.log文件
def init_forum_log():
    """初始化forum.log文件"""
    try:
        forum_log_file = LOG_DIR / "forum.log"
        with open(forum_log_file, 'w', encoding='utf-8') as f:
            start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"=== FoxTrends ForumEngine 系统初始化 - {start_time} ===\n")
        logger.info(f"ForumEngine: forum.log 已初始化")
    except Exception as e:
        logger.exception(f"ForumEngine: 初始化forum.log失败: {e}")


# 初始化forum.log
init_forum_log()


# 启动ForumEngine智能监控
def start_forum_engine():
    """启动ForumEngine论坛"""
    try:
        from ForumEngine.monitor import start_forum_monitoring
        logger.info("ForumEngine: 启动论坛...")
        success = start_forum_monitoring()
        if not success:
            logger.info("ForumEngine: 论坛启动失败")
        return success
    except Exception as e:
        logger.exception(f"ForumEngine: 启动论坛失败: {e}")
        return False


# 停止ForumEngine智能监控
def stop_forum_engine():
    """停止ForumEngine论坛"""
    try:
        from ForumEngine.monitor import stop_forum_monitoring
        # 使用 try-except 包装日志调用，避免在清理时出错
        try:
            logger.info("ForumEngine: 停止论坛...")
        except (ValueError, OSError):
            print("ForumEngine: 停止论坛...", file=sys.stderr)
        
        stop_forum_monitoring()
        
        try:
            logger.info("ForumEngine: 论坛已停止")
        except (ValueError, OSError):
            print("ForumEngine: 论坛已停止", file=sys.stderr)
    except Exception as e:
        try:
            logger.exception(f"ForumEngine: 停止论坛失败: {e}")
        except (ValueError, OSError):
            print(f"ForumEngine: 停止论坛失败: {e}", file=sys.stderr)


def parse_forum_log_line(line):
    """解析forum.log行内容，提取对话信息"""
    import re
    
    # 匹配格式: [时间] [来源] 内容
    pattern = r'\[(\d{2}:\d{2}:\d{2})\]\s*\[([A-Z_]+)\]\s*(.*)'
    match = re.match(pattern, line)
    
    if match:
        timestamp, source, content = match.groups()
        
        # 过滤掉系统消息和空内容
        if source == 'SYSTEM' or not content.strip():
            return None
        
        # 处理三个Agent的消息
        if source not in ['COMMUNITY_INSIGHT', 'CONTENT_ANALYSIS', 'TREND_DISCOVERY']:
            return None
        
        message_type = 'agent'
        sender = f'{source} Agent'
        
        return {
            'type': message_type,
            'sender': sender,
            'content': content.strip(),
            'timestamp': timestamp,
            'source': source
        }
    
    return None


# Forum日志监听器
def monitor_forum_log():
    """监听forum.log文件变化并推送到前端"""
    import time
    from pathlib import Path
    
    forum_log_file = LOG_DIR / "forum.log"
    last_position = 0
    processed_lines = set()
    
    if forum_log_file.exists():
        with open(forum_log_file, 'r', encoding='utf-8', errors='ignore') as f:
            existing_lines = f.readlines()
            for line in existing_lines:
                line_hash = hash(line.strip())
                processed_lines.add(line_hash)
            last_position = f.tell()
    
    while True:
        try:
            if forum_log_file.exists():
                with open(forum_log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    
                    if new_lines:
                        for line in new_lines:
                            line = line.rstrip('\n\r')
                            if line.strip():
                                line_hash = hash(line.strip())
                                
                                if line_hash in processed_lines:
                                    continue
                                
                                processed_lines.add(line_hash)
                                
                                parsed_message = parse_forum_log_line(line)
                                if parsed_message:
                                    socketio.emit('forum_message', parsed_message)
                                
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                formatted_line = f"[{timestamp}] {line}"
                                socketio.emit('console_output', {
                                    'app': 'forum',
                                    'line': formatted_line
                                })
                        
                        last_position = f.tell()
                        
                        if len(processed_lines) > 1000:
                            processed_lines.clear()
            
            time.sleep(1)
        except Exception as e:
            logger.error(f"Forum日志监听错误: {e}")
            time.sleep(5)


# 启动Forum日志监听线程
forum_monitor_thread = threading.Thread(target=monitor_forum_log, daemon=True)
forum_monitor_thread.start()


# 全局变量存储进程信息
processes = {
    'community_insight': {'process': None, 'port': 8501, 'status': 'stopped', 'output': []},
    'content_analysis': {'process': None, 'port': 8502, 'status': 'stopped', 'output': []},
    'trend_discovery': {'process': None, 'port': 8503, 'status': 'stopped', 'output': []},
    'forum': {'process': None, 'port': None, 'status': 'stopped', 'output': []}
}

# Dashboard应用脚本路径（待实现）
DASHBOARD_SCRIPTS = {
    'community_insight': 'Dashboard/community_insight_app.py',
    'content_analysis': 'Dashboard/content_analysis_app.py',
    'trend_discovery': 'Dashboard/trend_discovery_app.py'
}


def write_log_to_file(app_name, line):
    """将日志写入文件"""
    try:
        log_file_path = LOG_DIR / f"{app_name}.log"
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
            f.flush()
    except Exception as e:
        logger.error(f"Error writing log for {app_name}: {e}")


def read_log_from_file(app_name, tail_lines=None):
    """从文件读取日志"""
    try:
        log_file_path = LOG_DIR / f"{app_name}.log"
        if not log_file_path.exists():
            return []
        
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = [line.rstrip('\n\r') for line in lines if line.strip()]
            
            if tail_lines:
                return lines[-tail_lines:]
            return lines
    except Exception as e:
        logger.exception(f"Error reading log for {app_name}: {e}")
        return []


def initialize_system_components():
    """启动所有依赖组件"""
    logs = []
    errors = []
    
    # 初始化数据库
    if initialize_database():
        logs.append("数据库初始化成功")
    else:
        errors.append("数据库初始化失败")
        return False, logs, errors
    
    # 停止ForumEngine以避免文件冲突
    try:
        stop_forum_engine()
        logs.append("已停止 ForumEngine 监控器以避免文件冲突")
    except Exception as exc:
        message = f"停止 ForumEngine 时发生异常: {exc}"
        logs.append(message)
        logger.exception(message)
    
    processes['forum']['status'] = 'stopped'
    
    # 启动ForumEngine
    forum_started = False
    try:
        if start_forum_engine():
            processes['forum']['status'] = 'running'
            logs.append("ForumEngine 启动完成")
            forum_started = True
        else:
            errors.append("ForumEngine 启动失败")
    except Exception as exc:
        error_msg = f"ForumEngine 启动失败: {exc}"
        logs.append(error_msg)
        errors.append(error_msg)
    
    # 初始化ReportEngine
    if REPORT_ENGINE_AVAILABLE:
        try:
            if initialize_report_engine():
                logs.append("ReportEngine 初始化成功")
            else:
                msg = "ReportEngine 初始化失败"
                logs.append(msg)
                errors.append(msg)
        except Exception as exc:
            msg = f"ReportEngine 初始化异常: {exc}"
            logs.append(msg)
            errors.append(msg)
    
    if errors:
        cleanup_processes()
        processes['forum']['status'] = 'stopped'
        if forum_started:
            try:
                stop_forum_engine()
            except Exception:
                logger.exception("停止ForumEngine失败")
        return False, logs, errors
    
    return True, logs, []


def cleanup_processes():
    """清理所有进程"""
    processes['forum']['status'] = 'stopped'
    try:
        stop_forum_engine()
    except Exception:
        # 使用 print 避免在清理时触发 Loguru 错误
        print("停止ForumEngine失败", file=sys.stderr)
    _set_system_state(started=False, starting=False)
    
    # 清理 Loguru 处理器，避免写入已关闭的文件
    try:
        logger.remove()
    except Exception:
        pass


# 注册清理函数
atexit.register(cleanup_processes)


# ==================== Flask路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard页面"""
    return render_template('dashboard.html')


@app.route('/demand/<int:demand_id>')
def demand_detail(demand_id):
    """需求详情页面"""
    return render_template('demand_detail.html')


@app.route('/analysis')
def analysis():
    """需求分析页面"""
    return render_template('analysis.html')


@app.route('/api/status')
def get_status():
    """获取所有应用状态"""
    return jsonify({
        app_name: {
            'status': info['status'],
            'port': info['port']
        }
        for app_name, info in processes.items()
    })


@app.route('/api/start/<app_name>')
def start_app(app_name):
    """启动指定应用"""
    if app_name not in processes:
        return jsonify({'success': False, 'message': '未知应用'})
    
    if app_name == 'forum':
        try:
            if start_forum_engine():
                processes['forum']['status'] = 'running'
                return jsonify({'success': True, 'message': 'ForumEngine已启动'})
            else:
                return jsonify({'success': False, 'message': 'ForumEngine启动失败'})
        except Exception as exc:
            logger.exception("手动启动ForumEngine失败")
            return jsonify({'success': False, 'message': f'ForumEngine启动失败: {exc}'})
    
    return jsonify({'success': False, 'message': '该应用暂不支持启动操作'})


@app.route('/api/stop/<app_name>')
def stop_app(app_name):
    """停止指定应用"""
    if app_name not in processes:
        return jsonify({'success': False, 'message': '未知应用'})
    
    if app_name == 'forum':
        try:
            stop_forum_engine()
            processes['forum']['status'] = 'stopped'
            return jsonify({'success': True, 'message': 'ForumEngine已停止'})
        except Exception as exc:
            logger.exception("手动停止ForumEngine失败")
            return jsonify({'success': False, 'message': f'ForumEngine停止失败: {exc}'})
    
    return jsonify({'success': False, 'message': '该应用暂不支持停止操作'})


@app.route('/api/output/<app_name>')
def get_output(app_name):
    """获取应用输出"""
    if app_name not in processes:
        return jsonify({'success': False, 'message': '未知应用'})
    
    if app_name == 'forum':
        try:
            forum_log_content = read_log_from_file('forum')
            return jsonify({
                'success': True,
                'output': forum_log_content,
                'total_lines': len(forum_log_content)
            })
        except Exception as e:
            return jsonify({'success': False, 'message': f'读取forum日志失败: {str(e)}'})
    
    output_lines = read_log_from_file(app_name)
    
    return jsonify({
        'success': True,
        'output': output_lines
    })


@app.route('/api/forum/log')
def get_forum_log():
    """获取ForumEngine的forum.log内容"""
    try:
        forum_log_file = LOG_DIR / "forum.log"
        if not forum_log_file.exists():
            return jsonify({
                'success': True,
                'log_lines': [],
                'parsed_messages': [],
                'total_lines': 0
            })
        
        with open(forum_log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            lines = [line.rstrip('\n\r') for line in lines if line.strip()]
        
        parsed_messages = []
        for line in lines:
            parsed_message = parse_forum_log_line(line)
            if parsed_message:
                parsed_messages.append(parsed_message)
        
        return jsonify({
            'success': True,
            'log_lines': lines,
            'parsed_messages': parsed_messages,
            'total_lines': len(lines)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'读取forum.log失败: {str(e)}'})


# ==================== Dashboard API ====================

@app.route('/api/communities', methods=['GET'])
def list_communities():
    """获取所有社区列表"""
    try:
        from NicheEngine.engine import NicheEngine
        engine = NicheEngine()
        communities = engine.list_communities()
        
        return jsonify({
            'success': True,
            'communities': [
                {
                    'id': c.id,
                    'name': c.name,
                    'source_type': c.source_type,
                    'status': c.status
                }
                for c in communities
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/communities', methods=['POST'])
def add_community():
    """添加新社区"""
    try:
        data = request.get_json()
        name = data.get('name')
        source_type = data.get('source_type')
        config = data.get('config', {})
        
        if not name or not source_type:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        from NicheEngine.engine import NicheEngine
        engine = NicheEngine()
        community = engine.add_community(name, source_type, config)
        
        return jsonify({
            'success': True,
            'community': {
                'id': community.id,
                'name': community.name,
                'source_type': community.source_type,
                'status': community.status
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/demands', methods=['GET'])
def list_demands():
    """获取需求信号列表"""
    try:
        from database.db_manager import DatabaseManager
        from datetime import datetime
        
        db = DatabaseManager()
        
        # 获取查询参数
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        signal_type = request.args.get('signal_type', None)
        community_id = request.args.get('community_id', None, type=int)
        
        # 构建查询
        query = """
            SELECT 
                ds.id,
                ds.title,
                ds.content,
                ds.signal_type,
                ds.hotness_score,
                ds.sentiment_score,
                ds.source_url,
                ds.author,
                ds.discussion_count,
                ds.participant_count,
                ds.created_at,
                c.name as community_name,
                c.source_type as community_type
            FROM demand_signals ds
            LEFT JOIN communities c ON ds.community_id = c.id
            WHERE 1=1
        """
        params = []
        
        if signal_type:
            query += " AND ds.signal_type = %s"
            params.append(signal_type)
        
        if community_id:
            query += " AND ds.community_id = %s"
            params.append(community_id)
        
        query += " ORDER BY ds.hotness_score DESC, ds.created_at DESC"
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = db.execute_query(query, tuple(params))
        
        demands = []
        for row in results:
            demands.append({
                'id': row[0],
                'title': row[1],
                'content': row[2][:200] + '...' if row[2] and len(row[2]) > 200 else row[2],
                'signal_type': row[3],
                'hotness_score': float(row[4]) if row[4] else 0.0,
                'sentiment_score': float(row[5]) if row[5] else 0.0,
                'source_url': row[6],
                'author': row[7],
                'discussion_count': row[8] or 0,
                'participant_count': row[9] or 0,
                'created_at': row[10].strftime('%Y-%m-%d %H:%M:%S') if row[10] else '',
                'community': row[11] or 'Unknown',
                'community_type': row[12] or 'unknown'
            })
        
        return jsonify({
            'success': True,
            'demands': demands,
            'total': len(demands),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        logger.exception("获取需求列表失败")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/demands/<int:demand_id>', methods=['GET'])
def get_demand_detail(demand_id):
    """获取需求详情"""
    try:
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        
        query = """
            SELECT 
                ds.id,
                ds.title,
                ds.content,
                ds.signal_type,
                ds.hotness_score,
                ds.sentiment_score,
                ds.source_url,
                ds.author,
                ds.discussion_count,
                ds.participant_count,
                ds.created_at,
                ds.updated_at,
                c.name as community_name,
                c.source_type as community_type,
                c.id as community_id
            FROM demand_signals ds
            LEFT JOIN communities c ON ds.community_id = c.id
            WHERE ds.id = %s
        """
        
        results = db.execute_query(query, (demand_id,))
        
        if not results:
            return jsonify({'success': False, 'message': '需求不存在'}), 404
        
        row = results[0]
        demand = {
            'id': row[0],
            'title': row[1],
            'content': row[2],
            'signal_type': row[3],
            'hotness_score': float(row[4]) if row[4] else 0.0,
            'sentiment_score': float(row[5]) if row[5] else 0.0,
            'source_url': row[6],
            'author': row[7],
            'discussion_count': row[8] or 0,
            'participant_count': row[9] or 0,
            'created_at': row[10].strftime('%Y-%m-%d %H:%M:%S') if row[10] else '',
            'updated_at': row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else '',
            'community': row[12] or 'Unknown',
            'community_type': row[13] or 'unknown',
            'community_id': row[14]
        }
        
        return jsonify({
            'success': True,
            'demand': demand
        })
    except Exception as e:
        logger.exception(f"获取需求详情失败: {demand_id}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analysis/metrics', methods=['GET'])
def get_analysis_metrics():
    """获取分析指标"""
    try:
        from database.db_manager import DatabaseManager
        from datetime import datetime, timedelta
        
        db = DatabaseManager()
        days = request.args.get('days', 30, type=int)
        community_id = request.args.get('community_id', None, type=int)
        signal_type = request.args.get('signal_type', None)
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        prev_start_date = start_date - timedelta(days=days)
        
        # 构建查询
        where_clauses = ["ds.created_at >= %s AND ds.created_at <= %s"]
        params = [start_date, end_date]
        
        if community_id:
            where_clauses.append("ds.community_id = %s")
            params.append(community_id)
        
        if signal_type:
            where_clauses.append("ds.signal_type = %s")
            params.append(signal_type)
        
        where_clause = " AND ".join(where_clauses)
        
        # 当前周期指标
        current_query = f"""
            SELECT 
                COUNT(*) as total_demands,
                AVG(hotness_score) as avg_hotness,
                SUM(discussion_count) as total_discussions,
                SUM(participant_count) as total_participants,
                AVG(sentiment_score) as avg_sentiment
            FROM demand_signals ds
            WHERE {where_clause}
        """
        
        current_results = db.execute_query(current_query, tuple(params))
        
        # 上一周期指标（用于计算变化）
        prev_params = [prev_start_date, start_date] + params[2:]
        prev_results = db.execute_query(current_query, tuple(prev_params))
        
        current = current_results[0] if current_results else (0, 0, 0, 0, 0)
        prev = prev_results[0] if prev_results else (0, 0, 0, 0, 0)
        
        # 计算变化百分比
        def calc_change(current_val, prev_val):
            if prev_val == 0:
                return 0.0
            return ((current_val - prev_val) / prev_val) * 100
        
        metrics = {
            'total_demands': current[0] or 0,
            'avg_hotness': float(current[1]) if current[1] else 0.0,
            'total_discussions': current[2] or 0,
            'total_participants': current[3] or 0,
            'avg_sentiment': float(current[4]) if current[4] else 0.0,
            'changes': {
                'demands': calc_change(current[0] or 0, prev[0] or 0),
                'hotness': calc_change(current[1] or 0, prev[1] or 0),
                'discussions': calc_change(current[2] or 0, prev[2] or 0),
                'participants': calc_change(current[3] or 0, prev[3] or 0)
            }
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        logger.exception("获取分析指标失败")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analysis/trend', methods=['GET'])
def get_analysis_trend():
    """获取趋势数据"""
    try:
        from database.db_manager import DatabaseManager
        from datetime import datetime, timedelta
        
        db = DatabaseManager()
        days = request.args.get('days', 30, type=int)
        view = request.args.get('view', 'hotness')
        community_id = request.args.get('community_id', None, type=int)
        signal_type = request.args.get('signal_type', None)
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建查询
        where_clauses = ["ds.created_at >= %s AND ds.created_at <= %s"]
        params = [start_date, end_date]
        
        if community_id:
            where_clauses.append("ds.community_id = %s")
            params.append(community_id)
        
        if signal_type:
            where_clauses.append("ds.signal_type = %s")
            params.append(signal_type)
        
        where_clause = " AND ".join(where_clauses)
        
        # 根据视图类型选择聚合字段
        if view == 'hotness':
            agg_field = "AVG(hotness_score)"
        elif view == 'volume':
            agg_field = "COUNT(*)"
        elif view == 'sentiment':
            agg_field = "AVG(sentiment_score)"
        else:
            agg_field = "AVG(hotness_score)"
        
        query = f"""
            SELECT 
                DATE(ds.created_at) as date,
                {agg_field} as value
            FROM demand_signals ds
            WHERE {where_clause}
            GROUP BY DATE(ds.created_at)
            ORDER BY date
        """
        
        results = db.execute_query(query, tuple(params))
        
        dates = []
        values = []
        
        for row in results:
            dates.append(row[0].strftime('%Y-%m-%d'))
            values.append(float(row[1]) if row[1] else 0.0)
        
        return jsonify({
            'success': True,
            'dates': dates,
            'values': values
        })
    except Exception as e:
        logger.exception("获取趋势数据失败")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analysis/type-distribution', methods=['GET'])
def get_type_distribution():
    """获取需求类型分布"""
    try:
        from database.db_manager import DatabaseManager
        from datetime import datetime, timedelta
        
        db = DatabaseManager()
        days = request.args.get('days', 30, type=int)
        community_id = request.args.get('community_id', None, type=int)
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建查询
        where_clauses = ["created_at >= %s AND created_at <= %s"]
        params = [start_date, end_date]
        
        if community_id:
            where_clauses.append("community_id = %s")
            params.append(community_id)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
            SELECT 
                signal_type,
                COUNT(*) as count
            FROM demand_signals
            WHERE {where_clause}
            GROUP BY signal_type
        """
        
        results = db.execute_query(query, tuple(params))
        
        type_names = {
            'pain_point': '痛点',
            'feature_request': '功能请求',
            'bug_report': '问题反馈'
        }
        
        labels = []
        values = []
        
        for row in results:
            labels.append(type_names.get(row[0], row[0]))
            values.append(row[1])
        
        return jsonify({
            'success': True,
            'labels': labels,
            'values': values
        })
    except Exception as e:
        logger.exception("获取类型分布失败")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analysis/pain-points', methods=['GET'])
def get_pain_points():
    """获取关键痛点分析"""
    try:
        from database.db_manager import DatabaseManager
        from datetime import datetime, timedelta
        
        db = DatabaseManager()
        days = request.args.get('days', 30, type=int)
        community_id = request.args.get('community_id', None, type=int)
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建查询条件
        where_clauses = ["ds.created_at >= %s AND ds.created_at <= %s", "ds.signal_type = 'pain_point'"]
        params = [start_date, end_date]
        
        if community_id:
            where_clauses.append("ds.community_id = %s")
            params.append(community_id)
        
        where_clause = " AND ".join(where_clauses)
        
        # 查询痛点，按热度和讨论数排序
        query = f"""
            SELECT 
                ds.id,
                ds.title,
                ds.hotness_score,
                ds.discussion_count,
                ds.participant_count,
                ds.sentiment_score
            FROM demand_signals ds
            WHERE {where_clause}
            ORDER BY ds.hotness_score DESC, ds.discussion_count DESC
            LIMIT 5
        """
        
        results = db.execute_query(query, tuple(params))
        
        pain_points = []
        for row in results:
            hotness = float(row[2]) if row[2] else 0.0
            discussion_count = row[3] or 0
            
            # 计算严重程度
            if hotness >= 80:
                severity = 'high'
            elif hotness >= 60:
                severity = 'medium'
            else:
                severity = 'low'
            
            # 计算机会分数 (0-10)
            score = min(10, (hotness / 10) * 0.7 + (discussion_count / 10) * 0.3)
            
            pain_points.append({
                'id': row[0],
                'title': row[1],
                'evidence_count': discussion_count,
                'severity': severity,
                'score': round(score, 1)
            })
        
        return jsonify({
            'success': True,
            'pain_points': pain_points
        })
    except Exception as e:
        logger.exception("获取痛点分析失败")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analysis/insights', methods=['GET'])
def get_analysis_insights():
    """获取分析洞察"""
    try:
        from database.db_manager import DatabaseManager
        from datetime import datetime, timedelta
        
        db = DatabaseManager()
        days = request.args.get('days', 30, type=int)
        community_id = request.args.get('community_id', None, type=int)
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建基础查询条件
        where_clauses = ["created_at >= %s AND created_at <= %s"]
        params = [start_date, end_date]
        
        if community_id:
            where_clauses.append("community_id = %s")
            params.append(community_id)
        
        where_clause = " AND ".join(where_clauses)
        
        # 增长最快的需求
        fastest_query = f"""
            SELECT title, hotness_score
            FROM demand_signals
            WHERE {where_clause}
            ORDER BY hotness_score DESC
            LIMIT 1
        """
        fastest_result = db.execute_query(fastest_query, tuple(params))
        fastest = f'"{fastest_result[0][0]}" (热度: {fastest_result[0][1]:.1f})' if fastest_result else '暂无数据'
        
        # 最活跃的社区
        active_query = f"""
            SELECT c.name, COUNT(*) as demand_count
            FROM demand_signals ds
            JOIN communities c ON ds.community_id = c.id
            WHERE {where_clause}
            GROUP BY c.name
            ORDER BY demand_count DESC
            LIMIT 1
        """
        active_result = db.execute_query(active_query, tuple(params))
        active_community = f'{active_result[0][0]} ({active_result[0][1]} 个需求)' if active_result else '暂无数据'
        
        # 关键发现
        total_query = f"""
            SELECT COUNT(*), AVG(hotness_score)
            FROM demand_signals
            WHERE {where_clause}
        """
        total_result = db.execute_query(total_query, tuple(params))
        
        if total_result and total_result[0][0] > 0:
            total_count = total_result[0][0]
            avg_hotness = total_result[0][1]
            key_finding = f'在过去 {days} 天内发现 {total_count} 个需求，平均热度 {avg_hotness:.1f}'
        else:
            key_finding = '暂无足够数据进行分析'
        
        # 计算增长率
        prev_start = start_date - timedelta(days=days)
        prev_query = f"""
            SELECT COUNT(*)
            FROM demand_signals
            WHERE created_at >= %s AND created_at < %s
        """
        prev_result = db.execute_query(prev_query, (prev_start, start_date))
        prev_count = prev_result[0][0] if prev_result else 0
        current_count = total_result[0][0] if total_result else 0
        
        if prev_count > 0:
            growth_rate = round(((current_count - prev_count) / prev_count) * 100, 1)
        else:
            growth_rate = 0.0
        
        # 计算总讨论数和平均值
        mentions_query = f"""
            SELECT SUM(discussion_count), AVG(discussion_count)
            FROM demand_signals
            WHERE {where_clause}
        """
        mentions_result = db.execute_query(mentions_query, tuple(params))
        total_mentions = mentions_result[0][0] if mentions_result and mentions_result[0][0] else 0
        avg_mentions = round(mentions_result[0][1], 1) if mentions_result and mentions_result[0][1] else 0
        
        # 计算社区占比
        if active_result and total_result and total_result[0][0] > 0:
            community_percentage = round((active_result[0][1] / total_result[0][0]) * 100, 1)
            top_community = active_result[0][0]
        else:
            community_percentage = 0
            top_community = '暂无数据'
        
        insights = {
            'fastest': fastest,
            'active_community': active_community,
            'key_finding': key_finding,
            'growth_rate': growth_rate,
            'total_mentions': total_mentions,
            'avg_mentions': avg_mentions,
            'top_community': top_community,
            'community_percentage': community_percentage
        }
        
        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        logger.exception("获取分析洞察失败")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """生成需求分析报告"""
    try:
        data = request.get_json()
        demand_ids = data.get('demand_ids', [])
        report_type = data.get('report_type', 'demand_analysis')
        
        if not demand_ids:
            return jsonify({'success': False, 'message': '请选择至少一个需求'}), 400
        
        # 这里应该调用 ReportEngine 生成报告
        # 暂时返回模拟数据
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'message': '报告生成中，请稍候...'
        })
    except Exception as e:
        logger.exception("生成报告失败")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/reports/<report_id>/download', methods=['GET'])
def download_report(report_id):
    """下载报告"""
    try:
        # 这里应该返回实际的报告文件
        # 暂时返回错误
        return jsonify({'success': False, 'message': '报告下载功能开发中'}), 501
    except Exception as e:
        logger.exception(f"下载报告失败: {report_id}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """获取Dashboard统计数据"""
    try:
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        
        # 获取社区统计
        community_stats = db.execute_query("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active
            FROM communities
        """)
        
        # 获取需求统计
        demand_stats = db.execute_query("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN hotness_score >= 70 THEN 1 ELSE 0 END) as high_priority,
                AVG(hotness_score) as avg_hotness
            FROM demand_signals
        """)
        
        stats = {
            'total_communities': community_stats[0][0] if community_stats else 0,
            'active_communities': community_stats[0][1] if community_stats else 0,
            'total_demands': demand_stats[0][0] if demand_stats else 0,
            'high_priority_demands': demand_stats[0][1] if demand_stats else 0,
            'avg_hotness': float(demand_stats[0][2]) if demand_stats and demand_stats[0][2] else 0.0
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.exception("获取统计数据失败")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置值"""
    try:
        config_values = read_config_values()
        return jsonify({'success': True, 'config': config_values})
    except Exception as exc:
        logger.exception("读取配置失败")
        return jsonify({'success': False, 'message': f'读取配置失败: {exc}'}), 500


@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置值"""
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict) or not payload:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400
    
    updates = {}
    for key, value in payload.items():
        if key in CONFIG_KEYS:
            updates[key] = value if value is not None else ''
    
    if not updates:
        return jsonify({'success': False, 'message': '没有可更新的配置项'}), 400
    
    try:
        write_config_values(updates)
        updated_config = read_config_values()
        return jsonify({'success': True, 'config': updated_config})
    except Exception as exc:
        logger.exception("更新配置失败")
        return jsonify({'success': False, 'message': f'更新配置失败: {exc}'}), 500


@app.route('/api/system/status')
def get_system_status():
    """返回系统启动状态"""
    state = _get_system_state()
    return jsonify({
        'success': True,
        'started': state['started'],
        'starting': state['starting']
    })


@app.route('/api/system/start', methods=['POST'])
def start_system():
    """启动完整系统"""
    allowed, message = _prepare_system_start()
    if not allowed:
        return jsonify({'success': False, 'message': message}), 400
    
    try:
        success, logs, errors = initialize_system_components()
        if success:
            _set_system_state(started=True)
            return jsonify({'success': True, 'message': '系统启动成功', 'logs': logs})
        
        _set_system_state(started=False)
        return jsonify({
            'success': False,
            'message': '系统启动失败',
            'logs': logs,
            'errors': errors
        }), 500
    except Exception as exc:
        logger.exception("系统启动过程中出现异常")
        _set_system_state(started=False)
        return jsonify({'success': False, 'message': f'系统启动异常: {exc}'}), 500
    finally:
        _set_system_state(starting=False)


# ==================== SocketIO事件 ====================

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    emit('status', 'Connected to FoxTrends server')


@socketio.on('request_status')
def handle_status_request():
    """请求状态更新"""
    emit('status_update', {
        app_name: {
            'status': info['status'],
            'port': info['port']
        }
        for app_name, info in processes.items()
    })


if __name__ == '__main__':
    HOST = settings.HOST
    PORT = settings.PORT
    
    logger.info("FoxTrends 系统正在启动...")
    logger.info("等待配置确认，系统将在前端指令后启动组件...")
    logger.info(f"Flask服务器已启动，访问地址: http://{HOST}:{PORT}")
    
    try:
        socketio.run(app, host=HOST, port=PORT, debug=False)
    except KeyboardInterrupt:
        logger.info("\n正在关闭应用...")
        cleanup_processes()
