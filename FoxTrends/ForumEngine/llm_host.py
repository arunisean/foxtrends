"""
论坛主持人模块 - FoxTrends版本
使用LLM作为论坛主持人，引导多个agent进行需求分析讨论
"""

from openai import OpenAI
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from pathlib import Path

# 添加项目根目录到Python路径以导入config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class ForumHost:
    """
    论坛主持人类
    用于FoxTrends需求分析场景
    """
    
    def __init__(self, api_key: str = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化论坛主持人
        
        Args:
            api_key: 论坛主持人 LLM API 密钥
            base_url: 论坛主持人 LLM API 接口基础地址
            model_name: 模型名称
        """
        self.api_key = api_key or settings.FORUM_HOST_API_KEY

        if not self.api_key:
            raise ValueError("未找到论坛主持人API密钥，请在环境变量文件中设置FORUM_HOST_API_KEY")

        self.base_url = base_url or settings.FORUM_HOST_BASE_URL
        self.model = model_name or settings.FORUM_HOST_MODEL_NAME

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # 跟踪之前的总结以避免重复
        self.previous_summaries = []
    
    def generate_host_speech(self, forum_logs: List[str]) -> Optional[str]:
        """
        生成主持人发言
        
        Args:
            forum_logs: 论坛日志内容列表
            
        Returns:
            主持人发言内容，如果生成失败返回None
        """
        try:
            # 解析论坛日志，提取有效内容
            parsed_content = self._parse_forum_logs(forum_logs)
            
            if not parsed_content['agent_speeches']:
                print("ForumHost: 没有找到有效的agent发言")
                return None
            
            # 构建prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(parsed_content)
            
            # 调用API生成发言
            response = self._call_llm_api(system_prompt, user_prompt)
            
            if response["success"]:
                speech = response["content"]
                # 清理和格式化发言
                speech = self._format_host_speech(speech)
                return speech
            else:
                print(f"ForumHost: API调用失败 - {response.get('error', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"ForumHost: 生成发言时出错 - {str(e)}")
            return None
    
    def _parse_forum_logs(self, forum_logs: List[str]) -> Dict[str, Any]:
        """
        解析论坛日志，提取agent发言
        
        Returns:
            包含agent发言的字典
        """
        parsed = {
            'agent_speeches': []
        }
        
        for line in forum_logs:
            if not line.strip():
                continue
            
            # 解析时间戳和发言者
            match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s*\[(\w+)\]\s*(.+)', line)
            if match:
                timestamp, speaker, content = match.groups()
                
                # 跳过系统消息和HOST自己的发言
                if speaker in ['SYSTEM', 'HOST']:
                    continue
                
                # 记录agent发言（适配FoxTrends的Agent名称）
                if speaker in ['COMMUNITY_INSIGHT', 'CONTENT_ANALYSIS', 'TREND_DISCOVERY']:
                    # 处理转义的换行符
                    content = content.replace('\\n', '\n')
                    
                    parsed['agent_speeches'].append({
                        'timestamp': timestamp,
                        'speaker': speaker,
                        'content': content
                    })
        
        return parsed
    
    def _build_system_prompt(self) -> str:
        """构建系统prompt - 适配需求分析场景"""
        return """你是FoxTrends多垂直社区需求追踪系统的论坛主持人。你的职责是：

1. **需求梳理**：从各agent的发言中识别关键需求信号、用户痛点、功能请求
2. **引导讨论**：根据各agent的发言，引导深入讨论需求的优先级和可行性
3. **纠正错误**：结合不同agent的视角，如果发现需求理解错误或逻辑矛盾，请明确指出
4. **整合观点**：综合不同agent的视角，形成更全面的需求认识，找出共识和分歧
5. **趋势预测**：基于已有信息分析需求发展趋势，提出可能的机会点
6. **推进分析**：提出新的分析角度或需要关注的问题，引导后续讨论方向

**Agent介绍**：
- **COMMUNITY_INSIGHT Agent**：专注于社区历史数据的深度挖掘和分析，提供需求演变模式
- **CONTENT_ANALYSIS Agent**：擅长多模态内容分析，理解用户表达的需求和痛点
- **TREND_DISCOVERY Agent**：负责发现当前需求热点，分析需求优先级和竞品对比

**发言要求**：
1. **综合性**：每次发言控制在800字以内，内容应包括需求梳理、观点整合、问题引导等
2. **结构清晰**：使用明确的段落结构，包括需求梳理、观点对比、问题提出等部分
3. **深入分析**：不仅仅总结已有信息，还要提出深层次的见解和分析
4. **客观中立**：基于事实进行分析和判断，避免主观臆测
5. **前瞻性**：提出具有前瞻性的观点和建议，引导讨论向更深入的方向发展

**注意事项**：
- 保持专业性，重视数据和证据
- 对于需求优先级，应基于数据进行分析"""
    
    def _build_user_prompt(self, parsed_content: Dict[str, Any]) -> str:
        """构建用户prompt - 适配需求分析场景"""
        # 获取最近的发言
        recent_speeches = parsed_content['agent_speeches']
        
        # 构建发言摘要
        speeches_text = "\n\n".join([
            f"[{s['timestamp']}] {s['speaker']}:\n{s['content']}"
            for s in recent_speeches
        ])
        
        prompt = f"""最近的Agent发言记录：
{speeches_text}

请你作为论坛主持人，基于以上agent的发言进行综合分析，请按以下结构组织你的发言：

**一、需求信号梳理**
- 从各agent发言中识别关键需求信号、用户痛点、功能请求
- 按优先级和紧迫性整理需求
- 指出关键需求和重要趋势

**二、观点整合与对比分析**
- 综合三个Agent的视角和发现
- 指出不同数据源之间的共识与分歧
- 分析每个Agent的信息价值和互补性
- 如果发现需求理解错误或逻辑矛盾，请明确指出并给出理由

**三、深层次分析与优先级评估**
- 基于已有信息分析需求的深层原因和影响因素
- 评估需求的优先级和紧迫性，指出可能的机会点和风险
- 提出需要特别关注的方面和指标

**四、问题引导与讨论方向**
- 提出2-3个值得进一步深入探讨的关键问题
- 为后续分析提出具体的建议和方向
- 引导各Agent关注特定的数据维度或分析角度

请发表综合性的主持人发言（控制在800字以内），内容应包含以上四个部分，并保持逻辑清晰、分析深入、视角独特。"""
        
        return prompt
    
    def _call_llm_api(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """调用LLM API"""
        try:
            current_time = datetime.now().strftime("%Y年%m月%d日%H时%M分")
            time_prefix = f"今天的实际时间是{current_time}"
            if user_prompt:
                user_prompt = f"{time_prefix}\n{user_prompt}"
            else:
                user_prompt = time_prefix
                
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                top_p=0.9,
            )

            if response.choices:
                content = response.choices[0].message.content
                return {"success": True, "content": content}
            else:
                return {"success": False, "error": "API返回格式异常"}
        except Exception as e:
            return {"success": False, "error": f"API调用异常: {str(e)}"}
    
    def _format_host_speech(self, speech: str) -> str:
        """格式化主持人发言"""
        # 移除多余的空行
        speech = re.sub(r'\n{3,}', '\n\n', speech)
        
        # 移除可能的引号
        speech = speech.strip('"\'""''')
        
        return speech.strip()


# 创建全局实例
_host_instance = None

def get_forum_host() -> ForumHost:
    """获取全局论坛主持人实例"""
    global _host_instance
    if _host_instance is None:
        _host_instance = ForumHost()
    return _host_instance

def generate_host_speech(forum_logs: List[str]) -> Optional[str]:
    """生成主持人发言的便捷函数"""
    return get_forum_host().generate_host_speech(forum_logs)
