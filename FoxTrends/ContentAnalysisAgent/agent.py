"""
ContentAnalysisAgent - 内容分析Agent主类
多模态内容分析，理解用户表达的需求
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
import re
from openai import OpenAI
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class ContentAnalysisAgent:
    """
    内容分析Agent
    
    职责:
    - 多模态内容分析
    - 理解用户表达的需求
    - 提取痛点和功能请求
    - 情感分析
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化Agent"""
        self.config = config or {}
        self.api_key = self.config.get('api_key') or settings.CONTENT_ANALYSIS_API_KEY
        self.base_url = self.config.get('base_url') or settings.CONTENT_ANALYSIS_BASE_URL
        self.model_name = self.config.get('model_name') or settings.CONTENT_ANALYSIS_MODEL_NAME
        
        # 初始化LLM客户端
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None
            logger.warning("ContentAnalysisAgent: 未配置API密钥，将使用简化模式")
        
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
                'agent': 'ContentAnalysisAgent',
                'query': query,
                **analysis_result
            }
            
            self.state['results'].append(result)
            return result
            
        except Exception as e:
            logger.error(f"ContentAnalysisAgent: 分析失败 - {e}")
            return {
                'success': False,
                'agent': 'ContentAnalysisAgent',
                'query': query,
                'error': str(e)
            }
    
    def _analyze_with_llm(self, query: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM进行内容分析"""
        title = signal_data.get('title', '')
        content = signal_data.get('content', '')
        signal_type = signal_data.get('signal_type', '')
        
        system_prompt = """你是一个内容分析专家，专注于理解用户表达的需求、痛点和情感。

你的任务是：
1. 分析内容的情感倾向（正面/负面/中性）
2. 提取用户的核心痛点
3. 识别用户的功能请求
4. 评估需求的清晰度和可行性
5. 提取关键词和主题

请以JSON格式返回分析结果，包含以下字段：
{
  "analysis": "详细分析文本",
  "sentiment": {
    "label": "positive/negative/neutral",
    "score": 0.0-1.0,
    "reasoning": "情感判断理由"
  },
  "pain_points": [
    {"description": "痛点描述", "severity": "high/medium/low"}
  ],
  "feature_requests": [
    {"description": "功能请求描述", "priority": "high/medium/low"}
  ],
  "clarity_score": 0.0-1.0,
  "feasibility_score": 0.0-1.0,
  "keywords": ["关键词1", "关键词2"],
  "main_theme": "主题描述"
}"""
        
        user_prompt = f"""请分析以下需求信号的内容：

需求类型：{signal_type}
标题：{title}
内容：{content[:1000]}

请进行深入的内容分析，提取痛点、功能请求和情感信息。"""
        
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
            logger.error(f"ContentAnalysisAgent: LLM调用失败 - {e}")
            # 降级到规则分析
            return self._analyze_with_rules(query, signal_data)
    
    def _analyze_with_rules(self, query: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """基于规则的简化分析"""
        title = signal_data.get('title', '')
        content = signal_data.get('content', '')
        signal_type = signal_data.get('signal_type', '')
        
        text = f"{title} {content}".lower()
        
        # 情感分析
        sentiment = self._simple_sentiment_analysis(text)
        
        # 痛点提取
        pain_points = self._extract_pain_points(text, signal_type)
        
        # 功能请求提取
        feature_requests = self._extract_feature_requests(text, signal_type)
        
        # 关键词提取
        keywords = self._extract_keywords(text)
        
        return {
            'analysis': f'内容分析：该{signal_type}表达了用户的{sentiment["label"]}情感，包含{len(pain_points)}个痛点和{len(feature_requests)}个功能请求。',
            'sentiment': sentiment,
            'pain_points': pain_points,
            'feature_requests': feature_requests,
            'clarity_score': 0.7,
            'feasibility_score': 0.6,
            'keywords': keywords,
            'main_theme': signal_type
        }
    
    def _simple_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """简单的情感分析"""
        negative_keywords = ['bug', 'error', 'fail', 'broken', 'issue', 'problem', 'crash', 
                            '错误', '失败', '崩溃', '问题', '无法', '不能', '糟糕']
        positive_keywords = ['good', 'great', 'excellent', 'love', 'perfect', 'amazing',
                           '好', '很好', '优秀', '完美', '喜欢', '棒']
        
        negative_count = sum(1 for kw in negative_keywords if kw in text)
        positive_count = sum(1 for kw in positive_keywords if kw in text)
        
        if negative_count > positive_count:
            return {
                'label': 'negative',
                'score': min(0.9, 0.5 + negative_count * 0.1),
                'reasoning': '内容包含较多负面词汇'
            }
        elif positive_count > negative_count:
            return {
                'label': 'positive',
                'score': min(0.9, 0.5 + positive_count * 0.1),
                'reasoning': '内容包含较多正面词汇'
            }
        else:
            return {
                'label': 'neutral',
                'score': 0.5,
                'reasoning': '内容情感中性'
            }
    
    def _extract_pain_points(self, text: str, signal_type: str) -> List[Dict[str, str]]:
        """提取痛点"""
        pain_points = []
        
        # 基于信号类型判断
        if signal_type == 'bug_report':
            pain_points.append({
                'description': '系统存在功能性问题',
                'severity': 'high'
            })
        elif signal_type == 'pain_point':
            pain_points.append({
                'description': '用户体验存在明显痛点',
                'severity': 'high'
            })
        
        # 基于关键词提取
        if any(kw in text for kw in ['slow', 'lag', '慢', '卡顿']):
            pain_points.append({
                'description': '性能问题影响使用体验',
                'severity': 'medium'
            })
        
        if any(kw in text for kw in ['confusing', 'unclear', '不清楚', '困惑']):
            pain_points.append({
                'description': '功能不够清晰易懂',
                'severity': 'medium'
            })
        
        return pain_points if pain_points else [{'description': '需要进一步分析', 'severity': 'low'}]
    
    def _extract_feature_requests(self, text: str, signal_type: str) -> List[Dict[str, str]]:
        """提取功能请求"""
        feature_requests = []
        
        # 基于信号类型判断
        if signal_type == 'feature_request':
            feature_requests.append({
                'description': '用户明确提出功能需求',
                'priority': 'high'
            })
        
        # 基于关键词提取
        if any(kw in text for kw in ['add', 'support', 'need', 'want', '添加', '支持', '需要', '希望']):
            feature_requests.append({
                'description': '用户期望新增功能',
                'priority': 'medium'
            })
        
        if any(kw in text for kw in ['improve', 'enhance', 'better', '改进', '优化', '提升']):
            feature_requests.append({
                'description': '用户期望改进现有功能',
                'priority': 'medium'
            })
        
        return feature_requests if feature_requests else [{'description': '需要进一步分析', 'priority': 'low'}]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取：去除停用词后的高频词
        words = re.findall(r'\b\w+\b', text.lower())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     '的', '了', '是', '在', '有', '和', '与', '或', '但'}
        
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # 返回前5个关键词
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(5)]
    
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
