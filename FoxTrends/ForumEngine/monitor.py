"""
日志监控器 - FoxTrends版本
实时监控三个Agent的log文件中的SummaryNode输出
适配需求追踪场景
"""

import os
import time
import threading
from pathlib import Path
from datetime import datetime
import re
import json
from typing import Dict, Optional, List
from threading import Lock
from loguru import logger

# 导入论坛主持人模块
try:
    from .llm_host import generate_host_speech
    HOST_AVAILABLE = True
except ImportError:
    logger.exception("ForumEngine: 论坛主持人模块未找到，将以纯监控模式运行")
    HOST_AVAILABLE = False


class LogMonitor:
    """基于文件变化的智能日志监控器 - FoxTrends版本"""
   
    def __init__(self, log_dir: str = "logs"):
        """初始化日志监控器"""
        self.log_dir = Path(log_dir)
        self.forum_log_file = self.log_dir / "forum.log"
       
        # 要监控的日志文件（适配FoxTrends的Agent名称）
        self.monitored_logs = {
            'community_insight': self.log_dir / 'community_insight.log',
            'content_analysis': self.log_dir / 'content_analysis.log',
            'trend_discovery': self.log_dir / 'trend_discovery.log'
        }
       
        # 监控状态
        self.is_monitoring = False
        self.monitor_thread = None
        self.file_positions = {}
        self.file_line_counts = {}
        self.is_searching = False
        self.search_inactive_count = 0
        self.write_lock = Lock()
        
        # 主持人相关状态
        self.agent_speeches_buffer = []
        self.host_speech_threshold = 5
        self.is_host_generating = False
       
        # 目标节点识别模式（适配FoxTrends）
        self.target_node_patterns = [
            'FirstSummaryNode',
            'ReflectionSummaryNode',
            'CommunityInsightAgent.nodes.summary_node',
            'ContentAnalysisAgent.nodes.summary_node',
            'TrendDiscoveryAgent.nodes.summary_node',
            'nodes.summary_node',
            '正在生成首次段落总结',
            '正在生成反思总结',
        ]
        
        # 多行内容捕获状态
        self.capturing_json = {}
        self.json_buffer = {}
        self.json_start_line = {}
        self.in_error_block = {}
       
        # 确保logs目录存在
        self.log_dir.mkdir(exist_ok=True)
   
    def clear_forum_log(self):
        """清空forum.log文件"""
        try:
            if self.forum_log_file.exists():
                self.forum_log_file.unlink()
           
            start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.forum_log_file, 'w', encoding='utf-8') as f:
                pass
            self.write_to_forum_log(f"=== FoxTrends ForumEngine 监控开始 - {start_time} ===", "SYSTEM")
               
            logger.info(f"ForumEngine: forum.log 已清空并初始化")
            
            self.capturing_json = {}
            self.json_buffer = {}
            self.json_start_line = {}
            self.in_error_block = {}
            self.agent_speeches_buffer = []
            self.is_host_generating = False
           
        except Exception as e:
            logger.exception(f"ForumEngine: 清空forum.log失败: {e}")
   
    def write_to_forum_log(self, content: str, source: str = None):
        """写入内容到forum.log（线程安全）"""
        try:
            with self.write_lock:
                with open(self.forum_log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    content_one_line = content.replace('\n', '\\n').replace('\r', '\\r')
                    if source:
                        f.write(f"[{timestamp}] [{source}] {content_one_line}\n")
                    else:
                        f.write(f"[{timestamp}] {content_one_line}\n")
                    f.flush()
        except Exception as e:
            logger.exception(f"ForumEngine: 写入forum.log失败: {e}")
    
    def get_log_level(self, line: str) -> Optional[str]:
        """检测日志行的级别"""
        match = re.search(r'\|\s*(INFO|ERROR|WARNING|DEBUG|TRACE|CRITICAL)\s*\|', line)
        if match:
            return match.group(1)
        return None
    
    def is_target_log_line(self, line: str) -> bool:
        """检查是否是目标日志行（SummaryNode）"""
        log_level = self.get_log_level(line)
        if log_level == 'ERROR':
            return False
        
        if "| ERROR" in line or "| ERROR    |" in line:
            return False
        
        error_keywords = ["JSON解析失败", "JSON修复失败", "Traceback", "File \""]
        for keyword in error_keywords:
            if keyword in line:
                return False
        
        for pattern in self.target_node_patterns:
            if pattern in line:
                return True
        return False
    
    def is_valuable_content(self, line: str) -> bool:
        """判断是否是有价值的内容"""
        if "清理后的输出" in line:
            return True
        
        exclude_patterns = [
            "JSON解析失败", "JSON修复失败", "直接使用清理后的文本",
            "JSON解析成功", "成功生成", "已更新段落", "正在生成",
            "开始处理", "处理完成", "已读取HOST发言", "读取HOST发言失败",
            "未找到HOST发言", "调试输出", "信息记录"
        ]
        
        for pattern in exclude_patterns:
            if pattern in line:
                return False
        
        clean_line = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', line)
        clean_line = re.sub(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s*\|\s*[A-Z]+\s*\|\s*[^|]+?\s*-\s*', '', clean_line)
        clean_line = clean_line.strip()
        if len(clean_line) < 30:
            return False
            
        return True
    
    def is_json_start_line(self, line: str) -> bool:
        """判断是否是JSON开始行"""
        return "清理后的输出: {" in line
    
    def is_json_end_line(self, line: str) -> bool:
        """判断是否是JSON结束行"""
        stripped = line.strip()
        
        if re.match(r'^\[\d{2}:\d{2}:\d{2}\]', stripped):
            return False
        if re.match(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}', stripped):
            return False
        
        if stripped == "}" or stripped == "] }":
            return True
        return False
    
    def extract_json_content(self, json_lines: List[str]) -> Optional[str]:
        """从多行中提取并解析JSON内容"""
        try:
            json_start_idx = -1
            for i, line in enumerate(json_lines):
                if "清理后的输出: {" in line:
                    json_start_idx = i
                    break
            
            if json_start_idx == -1:
                return None
            
            first_line = json_lines[json_start_idx]
            json_start_pos = first_line.find("清理后的输出: {")
            if json_start_pos == -1:
                return None
            
            json_part = first_line[json_start_pos + len("清理后的输出: "):]
            
            if json_part.strip().endswith("}") and json_part.count("{") == json_part.count("}"):
                try:
                    json_obj = json.loads(json_part.strip())
                    return self.format_json_content(json_obj)
                except json.JSONDecodeError:
                    fixed_json = self.fix_json_string(json_part.strip())
                    if fixed_json:
                        try:
                            json_obj = json.loads(fixed_json)
                            return self.format_json_content(json_obj)
                        except json.JSONDecodeError:
                            pass
                    return None
            
            json_text = json_part
            for line in json_lines[json_start_idx + 1:]:
                clean_line = re.sub(r'^\[\d{2}:\d{2}:\d{2}\]\s*', '', line)
                clean_line = re.sub(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s*\|\s*[A-Z]+\s*\|\s*[^|]+?\s*-\s*', '', clean_line)
                json_text += clean_line
            
            try:
                json_obj = json.loads(json_text.strip())
                return self.format_json_content(json_obj)
            except json.JSONDecodeError:
                fixed_json = self.fix_json_string(json_text.strip())
                if fixed_json:
                    try:
                        json_obj = json.loads(fixed_json)
                        return self.format_json_content(json_obj)
                    except json.JSONDecodeError:
                        pass
                return None
            
        except Exception as e:
            return None
    
    def format_json_content(self, json_obj: dict) -> str:
        """格式化JSON内容为可读形式"""
        try:
            content = None
            
            if "updated_paragraph_latest_state" in json_obj:
                content = json_obj["updated_paragraph_latest_state"]
            elif "paragraph_latest_state" in json_obj:
                content = json_obj["paragraph_latest_state"]
            
            if content:
                return content
            
            return f"清理后的输出: {json.dumps(json_obj, ensure_ascii=False, indent=2)}"
            
        except Exception as e:
            logger.exception(f"ForumEngine: 格式化JSON时出错: {e}")
            return f"清理后的输出: {json.dumps(json_obj, ensure_ascii=False, indent=2)}"

    def extract_node_content(self, line: str) -> Optional[str]:
        """提取节点内容，去除时间戳、节点名称等前缀"""
        content = line
        
        match_old = re.search(r'\[\d{2}:\d{2}:\d{2}\]\s*(.+)', content)
        if match_old:
            content = match_old.group(1).strip()
        else:
            match_new = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s*\|\s*[A-Z]+\s*\|\s*[^|]+?\s*-\s*(.+)', content)
            if match_new:
                content = match_new.group(1).strip()
        
        if not content:
            return line.strip()
        
        content = re.sub(r'^\[.*?\]\s*', '', content)
        
        while re.match(r'^\[.*?\]\s*', content):
            content = re.sub(r'^\[.*?\]\s*', '', content)
        
        prefixes_to_remove = [
            "首次总结: ",
            "反思总结: ",
            "清理后的输出: "
        ]
        
        for prefix in prefixes_to_remove:
            if content.startswith(prefix):
                content = content[len(prefix):]
                break
        
        app_names = ['COMMUNITY_INSIGHT', 'CONTENT_ANALYSIS', 'TREND_DISCOVERY']
        for app_name in app_names:
            content = re.sub(rf'^{app_name}\s+', '', content, flags=re.IGNORECASE)
        
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
   
    def get_file_size(self, file_path: Path) -> int:
        """获取文件大小"""
        try:
            return file_path.stat().st_size if file_path.exists() else 0
        except:
            return 0
   
    def get_file_line_count(self, file_path: Path) -> int:
        """获取文件行数"""
        try:
            if not file_path.exists():
                return 0
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except:
            return 0
   
    def read_new_lines(self, file_path: Path, app_name: str) -> List[str]:
        """读取文件中的新行"""
        new_lines = []
       
        try:
            if not file_path.exists():
                return new_lines
           
            current_size = self.get_file_size(file_path)
            last_position = self.file_positions.get(app_name, 0)
           
            if current_size < last_position:
                last_position = 0
                self.capturing_json[app_name] = False
                self.json_buffer[app_name] = []
                self.in_error_block[app_name] = False
           
            if current_size > last_position:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.seek(last_position)
                    new_content = f.read()
                    new_lines = new_content.split('\n')
                   
                    self.file_positions[app_name] = f.tell()
                   
                    new_lines = [line.strip() for line in new_lines if line.strip()]
                   
        except Exception as e:
            logger.exception(f"ForumEngine: 读取{app_name}日志失败: {e}")
       
        return new_lines
   
    def process_lines_for_json(self, lines: List[str], app_name: str) -> List[str]:
        """处理行以捕获多行JSON内容"""
        captured_contents = []
        
        if app_name not in self.capturing_json:
            self.capturing_json[app_name] = False
            self.json_buffer[app_name] = []
        if app_name not in self.in_error_block:
            self.in_error_block[app_name] = False
        
        for line in lines:
            if not line.strip():
                continue
            
            log_level = self.get_log_level(line)
            if log_level == 'ERROR':
                self.in_error_block[app_name] = True
                if self.capturing_json[app_name]:
                    self.capturing_json[app_name] = False
                    self.json_buffer[app_name] = []
                continue
            elif log_level == 'INFO':
                self.in_error_block[app_name] = False
            
            if self.in_error_block[app_name]:
                if self.capturing_json[app_name]:
                    self.capturing_json[app_name] = False
                    self.json_buffer[app_name] = []
                continue
                
            is_target = self.is_target_log_line(line)
            is_json_start = self.is_json_start_line(line)
            
            if is_target and is_json_start:
                self.capturing_json[app_name] = True
                self.json_buffer[app_name] = [line]
                self.json_start_line[app_name] = line
                
                if line.strip().endswith("}"):
                    content = self.extract_json_content([line])
                    if content:
                        clean_content = self._clean_content_tags(content, app_name)
                        captured_contents.append(f"{clean_content}")
                    self.capturing_json[app_name] = False
                    self.json_buffer[app_name] = []
                    
            elif is_target and self.is_valuable_content(line):
                clean_content = self._clean_content_tags(self.extract_node_content(line), app_name)
                captured_contents.append(f"{clean_content}")
                    
            elif self.capturing_json[app_name]:
                self.json_buffer[app_name].append(line)
                
                cleaned_line = line.strip()
                cleaned_line = re.sub(r'^\[\d{2}:\d{2}:\d{2}\]\s*', '', cleaned_line)
                cleaned_line = re.sub(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s*\|\s*[A-Z]+\s*\|\s*[^|]+?\s*-\s*', '', cleaned_line)
                cleaned_line = cleaned_line.strip()
                
                if cleaned_line == "}" or cleaned_line == "] }":
                    content = self.extract_json_content(self.json_buffer[app_name])
                    if content:
                        clean_content = self._clean_content_tags(content, app_name)
                        captured_contents.append(f"{clean_content}")
                    
                    self.capturing_json[app_name] = False
                    self.json_buffer[app_name] = []
        
        return captured_contents
    
    def _trigger_host_speech(self):
        """触发主持人发言（同步执行）"""
        if not HOST_AVAILABLE or self.is_host_generating:
            return
        
        try:
            self.is_host_generating = True
            
            recent_speeches = self.agent_speeches_buffer[:5]
            if len(recent_speeches) < 5:
                self.is_host_generating = False
                return
            
            logger.info("ForumEngine: 正在生成主持人发言...")
            
            host_speech = generate_host_speech(recent_speeches)
            
            if host_speech:
                self.write_to_forum_log(host_speech, "HOST")
                logger.info(f"ForumEngine: 主持人发言已记录")
                self.agent_speeches_buffer = self.agent_speeches_buffer[5:]
            else:
                logger.error("ForumEngine: 主持人发言生成失败")
            
            self.is_host_generating = False
                
        except Exception as e:
            logger.exception(f"ForumEngine: 触发主持人发言时出错: {e}")
            self.is_host_generating = False
    
    def _clean_content_tags(self, content: str, app_name: str) -> str:
        """清理内容中的重复标签和多余前缀"""
        if not content:
            return content
            
        all_app_names = ['COMMUNITY_INSIGHT', 'CONTENT_ANALYSIS', 'TREND_DISCOVERY']
        
        for name in all_app_names:
            content = re.sub(rf'\[{name}\]\s*', '', content, flags=re.IGNORECASE)
            content = re.sub(rf'^{name}\s+', '', content, flags=re.IGNORECASE)
        
        content = re.sub(r'^\[.*?\]\s*', '', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
   
    def monitor_logs(self):
        """智能监控日志文件"""
        logger.info("ForumEngine: 论坛创建中...")
       
        for app_name, log_file in self.monitored_logs.items():
            self.file_line_counts[app_name] = self.get_file_line_count(log_file)
            self.file_positions[app_name] = self.get_file_size(log_file)
            self.capturing_json[app_name] = False
            self.json_buffer[app_name] = []
            self.in_error_block[app_name] = False
       
        while self.is_monitoring:
            try:
                any_growth = False
                any_shrink = False
                captured_any = False
               
                for app_name, log_file in self.monitored_logs.items():
                    current_lines = self.get_file_line_count(log_file)
                    previous_lines = self.file_line_counts.get(app_name, 0)
                   
                    if current_lines > previous_lines:
                        any_growth = True
                        new_lines = self.read_new_lines(log_file, app_name)
                       
                        if not self.is_searching:
                            for line in new_lines:
                                if line.strip() and self.is_target_log_line(line):
                                    if 'FirstSummaryNode' in line or '正在生成首次段落总结' in line:
                                        logger.info(f"ForumEngine: 在{app_name}中检测到第一次论坛发表内容")
                                        self.is_searching = True
                                        self.search_inactive_count = 0
                                        self.clear_forum_log()
                                        break
                       
                        if self.is_searching:
                            captured_contents = self.process_lines_for_json(new_lines, app_name)
                            
                            for content in captured_contents:
                                source_tag = app_name.upper()
                                self.write_to_forum_log(content, source_tag)
                                captured_any = True
                                
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                log_line = f"[{timestamp}] [{source_tag}] {content}"
                                self.agent_speeches_buffer.append(log_line)
                                
                                if len(self.agent_speeches_buffer) >= self.host_speech_threshold and not self.is_host_generating:
                                    self._trigger_host_speech()
                   
                    elif current_lines < previous_lines:
                        any_shrink = True
                        self.file_positions[app_name] = self.get_file_size(log_file)
                        self.capturing_json[app_name] = False
                        self.json_buffer[app_name] = []
                        self.in_error_block[app_name] = False
                   
                    self.file_line_counts[app_name] = current_lines
               
                if self.is_searching:
                    if any_shrink:
                        self.is_searching = False
                        self.search_inactive_count = 0
                        self.agent_speeches_buffer = []
                        self.is_host_generating = False
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.write_to_forum_log(f"=== FoxTrends ForumEngine 论坛结束 - {end_time} ===", "SYSTEM")
                    elif not any_growth and not captured_any:
                        self.search_inactive_count += 1
                        if self.search_inactive_count >= 7200:
                            logger.info("ForumEngine: 长时间无活动，结束论坛")
                            self.is_searching = False
                            self.search_inactive_count = 0
                            self.agent_speeches_buffer = []
                            self.is_host_generating = False
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            self.write_to_forum_log(f"=== FoxTrends ForumEngine 论坛结束 - {end_time} ===", "SYSTEM")
                    else:
                        self.search_inactive_count = 0
               
                time.sleep(1)
               
            except Exception as e:
                logger.exception(f"ForumEngine: 论坛记录中出错: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(2)
       
        logger.info("ForumEngine: 停止论坛日志文件")
   
    def start_monitoring(self):
        """开始智能监控"""
        if self.is_monitoring:
            logger.info("ForumEngine: 论坛已经在运行中")
            return False
       
        try:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_logs, daemon=True)
            self.monitor_thread.start()
           
            logger.info("ForumEngine: 论坛已启动")
            return True
           
        except Exception as e:
            logger.exception(f"ForumEngine: 启动论坛失败: {e}")
            self.is_monitoring = False
            return False
   
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            try:
                logger.info("ForumEngine: 论坛未运行")
            except (ValueError, OSError):
                # 在清理阶段，日志文件可能已关闭，使用 print 代替
                import sys
                print("ForumEngine: 论坛未运行", file=sys.stderr)
            return
       
        try:
            self.is_monitoring = False
           
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2)
           
            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.write_to_forum_log(f"=== FoxTrends ForumEngine 论坛结束 - {end_time} ===", "SYSTEM")
           
            logger.info("ForumEngine: 论坛已停止")
           
        except Exception as e:
            logger.exception(f"ForumEngine: 停止论坛失败: {e}")
   
    def get_forum_log_content(self) -> List[str]:
        """获取forum.log的内容"""
        try:
            if not self.forum_log_file.exists():
                return []
           
            with open(self.forum_log_file, 'r', encoding='utf-8') as f:
                return [line.rstrip('\n\r') for line in f.readlines()]
               
        except Exception as e:
            logger.exception(f"ForumEngine: 读取forum.log失败: {e}")
            return []

    def fix_json_string(self, json_text: str) -> str:
        """修复JSON字符串中的常见问题"""
        try:
            json.loads(json_text)
            return json_text
        except json.JSONDecodeError:
            pass
        
        try:
            fixed_text = ""
            i = 0
            in_string = False
            escape_next = False
            
            while i < len(json_text):
                char = json_text[i]
                
                if escape_next:
                    fixed_text += char
                    escape_next = False
                    i += 1
                    continue
                
                if char == '\\':
                    fixed_text += char
                    escape_next = True
                    i += 1
                    continue
                
                if char == '"' and not escape_next:
                    if in_string:
                        next_char_pos = i + 1
                        while next_char_pos < len(json_text) and json_text[next_char_pos].isspace():
                            next_char_pos += 1
                        
                        if next_char_pos < len(json_text):
                            next_char = json_text[next_char_pos]
                            if next_char in [':', ',', '}']:
                                in_string = False
                                fixed_text += char
                            else:
                                fixed_text += '\\"'
                        else:
                            in_string = False
                            fixed_text += char
                    else:
                        in_string = True
                        fixed_text += char
                else:
                    fixed_text += char
                
                i += 1
            
            try:
                json.loads(fixed_text)
                return fixed_text
            except json.JSONDecodeError:
                return None
                
        except Exception:
            return None


# 全局监控器实例
_monitor_instance = None

def get_monitor() -> LogMonitor:
    """获取全局监控器实例"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = LogMonitor()
    return _monitor_instance

def start_forum_monitoring():
    """启动ForumEngine智能监控"""
    return get_monitor().start_monitoring()

def stop_forum_monitoring():
    """停止ForumEngine监控"""
    get_monitor().stop_monitoring()

def get_forum_log():
    """获取forum.log内容"""
    return get_monitor().get_forum_log_content()
