"""
TrendDiscoveryAgent - 趋势发现Agent主类
发现新兴需求趋势，预测需求方向
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
from openai import OpenAI
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class TrendDiscoveryAgent:
    """
    趋势发现Agent
    
    职责:
    - 发现当前需求热点
    - 分析需求优先级
    - 预测需求趋势
    - 提供竞品对比分析
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化Agent"""
        self.config = config or {}
        self.api_key = self.config.get('api_key') or settings.TREND_DISCOVERY_AGENT_API_KEY
        self.base_url = self.config.get('base_url') or settings.TREND_DISCOVERY_AGENT_BASE_URL
        self.model_name = self.config.get('model_name') or settings.TREND_DISCOVERY_AGENT_MODEL_NAME
        
        # 初始化LLM客户端
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None
            logger.warning("TrendDiscoveryAgent: 未配置API密钥，将使用简化模式")
        
        self.state = {
            'query': None,
            'results': [],
            'summary': None
        }
    
    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """运行Agent主流程"""
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
                'agent': 'TrendDiscoveryAgent',
                'query': query,
                **analysis_result
            }
            
            self.state['results'].append(result)
            return result
            
        except Exception as e:
            logger.error(f"TrendDiscoveryAgent: 分析失败 - {e}")
            return {
                'success': False,
                'agent': 'TrendDiscoveryAgent',
                'query': query,
                'error': str(e)
            }
    
    def _analyze_with_llm(self, query: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM进行趋势分析"""
        title = signal_data.get('title', '')
        content = signal_data.get('content', '')
        signal_type = signal_data.get('signal_type', '')
        
        system_prompt = """你是一个需求趋势分析专家，专注于发现需求热点和预测趋势。

你的任务是：
1. 分析该需求在当前市场/社区中的热度
2. 评估需求的优先级（基于影响范围、紧急程度、实现难度）
3. 预测该需求的发展趋势
4. 识别相关的需求趋势
5. 提供竞品对比视角

请以JSON格式返回分析结果，包含以下字段：
{
  "analysis": "详细分析文本",
  "hotness_assessment": {
    "score": 0.0-1.0,
    "reasoning": "热度评估理由"
  },
  "priority_analysis": {
    "level": "high/medium/low",
    "impact_scope": "影响范围描述",
    "urgency": "紧急程度描述",
    "implementation_difficulty": "实现难度描述"
  },
  "trend_prediction": {
    "direction": "rising/stable/declining",
    "reasoning": "趋势预测理由",
    "time_horizon": "短期/中期/长期"
  },
  "related_trends": ["相关趋势1", "相关趋势2"],
  "competitive_insights": ["竞品洞察1", "竞品洞察2"],
  "recommendations": ["建议1", "建议2"]
}"""
        
        user_prompt = f"""请分析以下需求信号的趋势：

需求类型：{signal_type}
标题：{title}
内容：{content[:1000]}

请从趋势发现的角度进行分析，评估热度、优先级和发展方向。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"TrendDiscoveryAgent: LLM调用失败 - {e}")
            # 降级到规则分析
            return self._analyze_with_rules(query, signal_data)
    
    def _analyze_with_rules(self, query: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """基于规则的简化分析"""
        title = signal_data.get('title', '')
        content = signal_data.get('content', '')
        signal_type = signal_data.get('signal_type', '')
        discussion_count = signal_data.get('discussion_count', 0)
        participant_count = signal_data.get('participant_count', 0)
        
        text = f"{title} {content}".lower()
        
        # 热度评估
        hotness_score = self._calculate_hotness(discussion_count, participant_count, text)
        
        # 优先级分析
        priority = self._analyze_priority(signal_type, text, hotness_score)
        
        # 趋势预测
        trend = self._predict_trend(signal_type, hotness_score)
        
        # 相关趋势
        related_trends = self._identify_related_trends(text)
        
        return {
            'analysis': f'趋势分析：该{signal_type}当前热度为{hotness_score:.2f}，优先级为{priority["level"]}，预测趋势为{trend["direction"]}。',
            'hotness_assessment': {
                'score': hotness_score,
                'reasoning': f'基于{discussion_count}次讨论和{participant_count}位参与者'
            },
            'priority_analysis': priority,
            'trend_prediction': trend,
            'related_trends': related_trends,
            'competitive_insights': ['需要进一步的竞品分析'],
            'recommendations': self._generate_recommendations(priority['level'], trend['direction'])
        }
    
    def _calculate_hotness(self, discussion_count: int, participant_count: int, text: str) -> float:
        """计算热度分数"""
        # 基础分数：讨论和参与者
        base_score = min(1.0, (discussion_count * 0.01 + participant_count * 0.02))
        
        # 关键词加成
        hot_keywords = ['urgent', 'critical', 'important', '紧急', '重要', '关键']
        keyword_bonus = 0.1 if any(kw in text for kw in hot_keywords) else 0
        
        return min(1.0, base_score + keyword_bonus)
    
    def _analyze_priority(self, signal_type: str, text: str, hotness_score: float) -> Dict[str, str]:
        """分析优先级"""
        # 基于信号类型和热度
        if signal_type == 'bug_report' or hotness_score > 0.7:
            level = 'high'
            impact_scope = '影响较大范围用户'
            urgency = '需要尽快处理'
        elif hotness_score > 0.4:
            level = 'medium'
            impact_scope = '影响部分用户'
            urgency = '建议在近期处理'
        else:
            level = 'low'
            impact_scope = '影响范围有限'
            urgency = '可以排期处理'
        
        # 实现难度评估
        if any(kw in text for kw in ['simple', 'easy', '简单', '容易']):
            difficulty = '实现难度较低'
        elif any(kw in text for kw in ['complex', 'difficult', '复杂', '困难']):
            difficulty = '实现难度较高'
        else:
            difficulty = '实现难度中等'
        
        return {
            'level': level,
            'impact_scope': impact_scope,
            'urgency': urgency,
            'implementation_difficulty': difficulty
        }
    
    def _predict_trend(self, signal_type: str, hotness_score: float) -> Dict[str, str]:
        """预测趋势"""
        if hotness_score > 0.6:
            direction = 'rising'
            reasoning = '需求热度持续上升，关注度增加'
            time_horizon = '短期'
        elif hotness_score > 0.3:
            direction = 'stable'
            reasoning = '需求保持稳定关注'
            time_horizon = '中期'
        else:
            direction = 'declining'
            reasoning = '需求关注度较低'
            time_horizon = '长期'
        
        return {
            'direction': direction,
            'reasoning': reasoning,
            'time_horizon': time_horizon
        }
    
    def _identify_related_trends(self, text: str) -> List[str]:
        """识别相关趋势"""
        trends = []
        
        if any(kw in text for kw in ['ai', 'ml', 'machine learning', '人工智能', '机器学习']):
            trends.append('AI/ML集成趋势')
        
        if any(kw in text for kw in ['mobile', 'app', '移动', '手机']):
            trends.append('移动化趋势')
        
        if any(kw in text for kw in ['performance', 'speed', '性能', '速度']):
            trends.append('性能优化趋势')
        
        if any(kw in text for kw in ['ui', 'ux', 'design', '界面', '体验']):
            trends.append('用户体验改进趋势')
        
        return trends if trends else ['通用功能改进趋势']
    
    def _generate_recommendations(self, priority_level: str, trend_direction: str) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if priority_level == 'high':
            recommendations.append('建议优先排期处理')
            recommendations.append('建议与用户保持密切沟通')
        
        if trend_direction == 'rising':
            recommendations.append('建议密切关注需求演变')
            recommendations.append('建议评估资源投入')
        
        recommendations.append('建议进行更深入的用户调研')
        
        return recommendations
    
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
