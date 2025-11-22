"""
ForumEngine 属性测试
验证 ForumEngine 的协作机制、发言记录和持久化功能
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime


class TestForumEngineProperties:
    """ForumEngine 属性测试类"""
    
    def setup_method(self):
        """测试前设置"""
        # 创建临时日志目录
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir)
    
    def teardown_method(self):
        """测试后清理"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_forum_engine_collaboration_mechanism(self):
        """
        属性 3: ForumEngine 协作机制保留
        验证需求: 2.4
        
        对于任何 Agent 生成的 SummaryNode 输出，ForumEngine 应该能够
        正确监控、记录并触发主持人发言
        """
        from ForumEngine.monitor import LogMonitor
        
        # 创建监控器实例
        monitor = LogMonitor(log_dir=str(self.log_dir))
        
        # 验证监控器初始化
        assert monitor.log_dir == self.log_dir
        assert monitor.forum_log_file == self.log_dir / "forum.log"
        
        # 验证监控的日志文件配置正确
        assert 'community_insight' in monitor.monitored_logs
        assert 'content_analysis' in monitor.monitored_logs
        assert 'trend_discovery' in monitor.monitored_logs
        
        # 验证目标节点模式包含必要的模式
        assert 'FirstSummaryNode' in monitor.target_node_patterns
        assert 'ReflectionSummaryNode' in monitor.target_node_patterns
        
        # 验证主持人相关状态初始化
        assert monitor.agent_speeches_buffer == []
        assert monitor.host_speech_threshold == 5
        assert monitor.is_host_generating == False
        
        print("✓ ForumEngine 协作机制保留测试通过")
    
    def test_agent_speech_recording_completeness(self):
        """
        属性 15: Agent 发言记录完整性
        验证需求: 6.1
        
        对于任何 Agent 的 SummaryNode 输出，ForumEngine 应该将其完整记录到
        forum.log，并且记录包含时间戳和 Agent 标识
        """
        from ForumEngine.monitor import LogMonitor
        
        monitor = LogMonitor(log_dir=str(self.log_dir))
        
        # 测试写入功能
        test_content = "这是一条测试发言内容"
        test_source = "COMMUNITY_INSIGHT"
        
        monitor.write_to_forum_log(test_content, test_source)
        
        # 验证文件存在
        assert monitor.forum_log_file.exists()
        
        # 读取并验证内容
        with open(monitor.forum_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        assert len(lines) > 0
        last_line = lines[-1].strip()
        
        # 验证格式：[时间戳] [来源] 内容
        import re
        pattern = r'\[(\d{2}:\d{2}:\d{2})\]\s*\[(\w+)\]\s*(.+)'
        match = re.match(pattern, last_line)
        
        assert match is not None, f"日志格式不正确: {last_line}"
        timestamp, source, content = match.groups()
        
        # 验证时间戳格式
        assert re.match(r'\d{2}:\d{2}:\d{2}', timestamp)
        
        # 验证来源标识
        assert source == test_source
        
        # 验证内容（注意换行符被转义）
        assert test_content.replace('\n', '\\n') in content
        
        print("✓ Agent 发言记录完整性测试通过")
    
    def test_discussion_record_persistence(self):
        """
        属性 16: 讨论记录持久化
        验证需求: 6.5
        
        对于任何 ForumEngine 的讨论会话，所有 Agent 发言和主持人总结
        应该被持久化到 forum.log 文件
        """
        from ForumEngine.monitor import LogMonitor
        
        monitor = LogMonitor(log_dir=str(self.log_dir))
        
        # 模拟多个Agent发言
        test_speeches = [
            ("COMMUNITY_INSIGHT", "社区历史数据显示用户对功能A有强烈需求"),
            ("CONTENT_ANALYSIS", "内容分析表明用户痛点集中在性能问题"),
            ("TREND_DISCOVERY", "趋势预测显示需求B将在未来3个月内增长"),
            ("HOST", "综合各Agent观点，我们应该优先关注功能A和性能优化"),
        ]
        
        # 写入所有发言
        for source, content in test_speeches:
            monitor.write_to_forum_log(content, source)
        
        # 验证文件存在
        assert monitor.forum_log_file.exists()
        
        # 读取并验证所有内容都被持久化
        log_content = monitor.get_forum_log_content()
        
        assert len(log_content) >= len(test_speeches)
        
        # 验证每条发言都被记录
        for source, content in test_speeches:
            # 查找包含该来源和内容的行
            found = False
            for line in log_content:
                if f"[{source}]" in line and content.replace('\n', '\\n') in line:
                    found = True
                    break
            assert found, f"未找到来源为 {source} 的发言: {content}"
        
        # 验证文件在重新读取后内容一致
        log_content_2 = monitor.get_forum_log_content()
        assert log_content == log_content_2
        
        print("✓ 讨论记录持久化测试通过")
    
    def test_forum_log_initialization(self):
        """测试 forum.log 初始化"""
        from ForumEngine.monitor import LogMonitor
        
        monitor = LogMonitor(log_dir=str(self.log_dir))
        monitor.clear_forum_log()
        
        # 验证文件被创建
        assert monitor.forum_log_file.exists()
        
        # 验证包含初始化标记
        content = monitor.get_forum_log_content()
        assert len(content) > 0
        assert "ForumEngine 监控开始" in content[0]
        
        print("✓ Forum log 初始化测试通过")
    
    def test_target_node_pattern_recognition(self):
        """测试目标节点模式识别"""
        from ForumEngine.monitor import LogMonitor
        
        monitor = LogMonitor(log_dir=str(self.log_dir))
        
        # 测试正面案例
        positive_cases = [
            "2024-01-01 10:00:00.000 | INFO | CommunityInsightAgent.nodes.summary_node - 正在生成首次段落总结",
            "2024-01-01 10:00:00.000 | INFO | ContentAnalysisAgent.nodes.summary_node - 正在生成反思总结",
            "[10:00:00] FirstSummaryNode - 开始处理",
            "[10:00:00] ReflectionSummaryNode - 开始处理",
        ]
        
        for case in positive_cases:
            assert monitor.is_target_log_line(case), f"应该识别为目标行: {case}"
        
        # 测试负面案例
        negative_cases = [
            "2024-01-01 10:00:00.000 | ERROR | module - JSON解析失败",
            "2024-01-01 10:00:00.000 | INFO | SearchNode - 搜索完成",
            "[10:00:00] 普通日志信息",
        ]
        
        for case in negative_cases:
            assert not monitor.is_target_log_line(case), f"不应该识别为目标行: {case}"
        
        print("✓ 目标节点模式识别测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
