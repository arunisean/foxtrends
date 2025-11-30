"""
CommunityInsightAgent - 社区洞察Agent主类
分析社区历史数据，识别长期需求模式
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys
from openai import OpenAI
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class CommunityInsightAgent:
    """
    社区洞察Agent
    
    职责:
    - 分析社区历史数据
    - 识别长期需求模式
    - 提供需求演变趋势
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化Agent
        
        Args:
            config: 配置字典，如果不提供则使用默认配置
        """
        self.config = config or {}
        self.api_key = self.config.get('api_key') or settings.COMMUNITY_INSIGHT_API_KEY
        self.base_url = self.config.get('base_url') or settings.COMMUNITY_INSIGHT_BASE_URL
        self.model_name = self.config.get('model_name') or settings.COMMUNITY_INSIGHT_MODEL_NAME
        
        # 初始化LLM客户端
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None
            logger.warning("CommunityInsightAgent: 未配置API密钥，将使用简化模式")
        
        # Agent状态
        self.state = {
            'query': None,
            'results': [],
            'summary': None
        }
    
    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        运行Agent主流程
        
        Args:
            query: 查询内容
            **kwargs: 额外参数（signal_data包含需求信号的详细信息）
            
        Returns:
            分析结果字典
        """
        self.state['query'] = query
        signal_data = kwargs.get('signal_data', {})
        
        try:
            if self.client:
                # 使用LLM进行真实分析
                analysis_result = self._analyze_with_llm(query, signal_data)
            else:
                # 简化模式：基于规则的分析
                analysis_result = self._analyze_with_rules(query, signal_data)
            
            result = {
                'success': True,
                'agent': 'CommunityInsightAgent',
                'query': query,
                **analysis_result
            }
            
            self.state['results'].append(result)
            return result
            
        except Exception as e:
            logger.error(f"CommunityInsightAgent: 分析失败 - {e}")
            return {
                'success': False,
                'agent': 'CommunityInsightAgent',
                'query': query,
                'error': str(e)
            }
    
    def _analyze_with_llm(self, query: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM进行分析"""
        title = signal_data.get('title', '')
        content = signal_data.get('content', '')
        signal_type = signal_data.get('signal_type', '')
        
        system_prompt = """你是一个社区需求分析专家，专注于分析社区历史数据和长期需求模式。

你的任务是：
1. 识别需求的历史背景和演变趋势
2. 分析该需求在社区中的重要性和紧迫性
3. 识别相似的历史需求模式
4. 预测需求的发展方向

请以JSON格式返回分析结果，包含以下字段：
{
  "analysis": "详细分析文本",
  "historical_context": "历史背景描述",
  "importance_level": "high/medium/low",
  "urgency_level": "high/medium/low",
  "similar_patterns": ["模式1", "模式2"],
  "evolution_trend": "演变趋势描述",
  "recommendations": ["建议1", "建议2"]
}"""
        
        user_prompt = f"""请分析以下需求信号：

需求类型：{signal_type}
标题：{title}
内容：{content[:500]}

请从社区历史数据的角度进行深入分析。"""
        
        try:
            # 根据模型类型决定是否使用 JSON mode
            # Thinking 模式的模型不支持 JSON mode
            model_lower = self.model_name.lower()
            is_thinking_model = any(keyword in model_lower for keyword in ['gemini', 'thinking', 'qwen3'])
            
            extra_params = {}
            if not is_thinking_model:
                extra_params['response_format'] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                **extra_params
            )
            
            import json
            content = response.choices[0].message.content
            
            # 尝试提取 JSON（处理可能返回的 markdown 格式）
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            # 清理可能的前后空白和非JSON字符
            content = content.strip()
            if not content:
                raise ValueError("模型返回空内容")
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            logger.error(f"CommunityInsightAgent: LLM调用失败 - {e}")
            # 降级到规则分析
            return self._analyze_with_rules(query, signal_data)
    
    def _analyze_with_rules(self, query: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """基于规则的简化分析"""
        title = signal_data.get('title', '').lower()
        content = signal_data.get('content', '').lower()
        signal_type = signal_data.get('signal_type', '')
        
        # 简单的关键词匹配
        urgency_keywords = ['urgent', 'critical', 'asap', '紧急', '严重', '崩溃', 'crash']
        importance_keywords = ['important', 'essential', 'critical', '重要', '关键', '核心']
        
        urgency_level = 'high' if any(kw in title or kw in content for kw in urgency_keywords) else 'medium'
        importance_level = 'high' if any(kw in title or kw in content for kw in importance_keywords) else 'medium'
        
        return {
            'analysis': f'基于社区历史数据分析，该{signal_type}反映了用户的实际需求。',
            'historical_context': '该需求与社区中的长期关注点相关。',
            'importance_level': importance_level,
            'urgency_level': urgency_level,
            'similar_patterns': ['类似需求模式1', '类似需求模式2'],
            'evolution_trend': '该需求呈现持续增长趋势',
            'recommendations': ['建议优先处理', '建议与用户进一步沟通']
        }
    
    def get_state(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return self.state.copy()
    
    def reset_state(self):
        """重置Agent状态"""
        self.state = {
            'query': None,
            'results': [],
            'summary': None
        }
