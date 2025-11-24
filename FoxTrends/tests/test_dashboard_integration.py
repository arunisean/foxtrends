"""
Dashboard 集成测试
测试前后端交互、实时数据更新和图表渲染
"""
import pytest
import json
from datetime import datetime, timedelta


class TestDashboardIntegration:
    """Dashboard 集成测试类"""
    
    def test_homepage_renders_correctly(self, client):
        """测试首页正确渲染"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'FoxTrends' in response.data
        assert b'Dashboard' in response.data
    
    def test_dashboard_page_renders(self, client):
        """测试 Dashboard 页面渲染"""
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'unified_dashboard' in response.data or b'FoxTrends' in response.data
    
    def test_demand_detail_page_renders(self, client):
        """测试需求详情页面渲染"""
        response = client.get('/demand/1')
        assert response.status_code == 200
        assert b'demand' in response.data.lower()
    
    def test_analysis_page_renders(self, client):
        """测试分析页面渲染"""
        response = client.get('/analysis')
        assert response.status_code == 200
        data_lower = response.data.lower()
        assert b'analysis' in data_lower or '分析'.encode('utf-8') in response.data
    
    def test_api_system_status_integration(self, client):
        """测试系统状态 API 集成"""
        response = client.get('/api/system/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'started' in data
        assert 'database_connected' in data
        assert 'active_tasks_count' in data
        assert 'last_update' in data
    
    def test_api_dashboard_stats_integration(self, client):
        """测试 Dashboard 统计 API 集成"""
        response = client.get('/api/dashboard/stats')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'stats' in data
        
        stats = data['stats']
        assert 'total_communities' in stats
        assert 'active_communities' in stats
        assert 'total_demands' in stats
        assert 'high_priority_demands' in stats
        assert 'avg_hotness' in stats
    
    def test_api_communities_list_integration(self, client):
        """测试社区列表 API 集成"""
        response = client.get('/api/communities')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'communities' in data
        assert isinstance(data['communities'], list)
    
    def test_api_demands_list_integration(self, client):
        """测试需求列表 API 集成"""
        response = client.get('/api/demands?limit=10')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'demands' in data
        assert isinstance(data['demands'], list)
        assert 'total' in data
        assert 'limit' in data
        assert data['limit'] == 10
    
    def test_api_analysis_metrics_integration(self, client):
        """测试分析指标 API 集成"""
        response = client.get('/api/analysis/metrics?days=30')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'metrics' in data
        
        metrics = data['metrics']
        assert 'total_demands' in metrics
        assert 'avg_hotness' in metrics
        assert 'total_discussions' in metrics
        assert 'total_participants' in metrics
        assert 'avg_sentiment' in metrics
        assert 'changes' in metrics
    
    def test_api_analysis_trend_integration(self, client):
        """测试趋势数据 API 集成"""
        response = client.get('/api/analysis/trend?days=30&view=hotness')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'dates' in data
        assert 'values' in data
        assert isinstance(data['dates'], list)
        assert isinstance(data['values'], list)
    
    def test_api_type_distribution_integration(self, client):
        """测试类型分布 API 集成"""
        response = client.get('/api/analysis/type-distribution?days=30')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'labels' in data
        assert 'values' in data
        assert isinstance(data['labels'], list)
        assert isinstance(data['values'], list)
    
    def test_api_pain_points_integration(self, client):
        """测试痛点分析 API 集成"""
        response = client.get('/api/analysis/pain-points?days=30')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'pain_points' in data
        assert isinstance(data['pain_points'], list)
    
    def test_api_insights_integration(self, client):
        """测试洞察 API 集成"""
        response = client.get('/api/analysis/insights?days=30')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'insights' in data
        
        insights = data['insights']
        assert 'fastest' in insights
        assert 'active_community' in insights
        assert 'key_finding' in insights
        assert 'growth_rate' in insights
    
    def test_api_monitoring_logs_integration(self, client):
        """测试监控日志 API 集成"""
        response = client.get('/api/monitoring/logs?limit=20')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'logs' in data
        assert isinstance(data['logs'], list)
    
    def test_add_community_workflow(self, client):
        """测试添加社区的完整工作流"""
        # 1. 添加社区
        community_data = {
            'name': 'Test Integration Community',
            'source_type': 'reddit',
            'config': {'subreddit': 'test'}
        }
        
        response = client.post(
            '/api/communities',
            data=json.dumps(community_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'community' in data
        community_id = data['community']['id']
        
        # 2. 验证社区出现在列表中
        response = client.get('/api/communities')
        data = response.get_json()
        assert data['success'] is True
        
        community_names = [c['name'] for c in data['communities']]
        assert 'Test Integration Community' in community_names
        
        # 3. 获取社区统计
        response = client.get(f'/api/communities/{community_id}/stats')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'stats' in data
    
    def test_demand_detail_workflow(self, client, sample_demand):
        """测试需求详情查看工作流"""
        # 1. 获取需求列表
        response = client.get('/api/demands?limit=10')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['demands']) > 0
        
        # 2. 获取第一个需求的详情
        demand_id = data['demands'][0]['id']
        response = client.get(f'/api/demands/{demand_id}')
        assert response.status_code == 200
        
        detail_data = response.get_json()
        assert detail_data['success'] is True
        assert 'demand' in detail_data
        assert detail_data['demand']['id'] == demand_id
    
    def test_analysis_page_data_flow(self, client, analysis_test_data):
        """测试分析页面的数据流"""
        # 确保有测试数据
        assert len(analysis_test_data['demands']) > 0
        assert len(analysis_test_data['communities']) > 0
        
        # 1. 获取指标
        response = client.get('/api/analysis/metrics?days=30')
        assert response.status_code == 200
        metrics_data = response.get_json()
        assert metrics_data['success'] is True
        
        # 2. 获取趋势
        response = client.get('/api/analysis/trend?days=30&view=hotness')
        assert response.status_code == 200
        trend_data = response.get_json()
        assert trend_data['success'] is True
        
        # 3. 获取类型分布
        response = client.get('/api/analysis/type-distribution?days=30')
        assert response.status_code == 200
        dist_data = response.get_json()
        assert dist_data['success'] is True
        
        # 4. 获取痛点
        response = client.get('/api/analysis/pain-points?days=30')
        assert response.status_code == 200
        pain_data = response.get_json()
        assert pain_data['success'] is True
        
        # 5. 获取洞察
        response = client.get('/api/analysis/insights?days=30')
        assert response.status_code == 200
        insights_data = response.get_json()
        assert insights_data['success'] is True
    
    def test_filter_functionality(self, client):
        """测试筛选功能"""
        # 测试按社区筛选
        response = client.get('/api/demands?community_id=1&limit=10')
        assert response.status_code == 200
        
        # 测试按类型筛选
        response = client.get('/api/demands?signal_type=pain_point&limit=10')
        assert response.status_code == 200
        
        # 测试组合筛选
        response = client.get('/api/demands?community_id=1&signal_type=pain_point&limit=10')
        assert response.status_code == 200
    
    def test_pagination(self, client):
        """测试分页功能"""
        # 第一页
        response = client.get('/api/demands?limit=5&offset=0')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['limit'] == 5
        assert data['offset'] == 0
        
        # 第二页
        response = client.get('/api/demands?limit=5&offset=5')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['offset'] == 5
    
    def test_analysis_page_has_report_generation_ui(self, client):
        """测试分析页面包含时间范围报告生成UI"""
        response = client.get('/analysis')
        assert response.status_code == 200
        
        # 检查页面包含报告生成按钮
        assert '生成时间范围报告'.encode('utf-8') in response.data
        
        # 检查页面包含日期选择器
        assert b'start-date-filter' in response.data
        assert b'end-date-filter' in response.data
        
        # 检查页面包含自定义时间范围按钮
        assert '自定义'.encode('utf-8') in response.data
    
    def test_time_range_report_api_with_valid_dates(self, client, analysis_test_data):
        """测试时间范围报告API - 有效日期"""
        # 确保有测试数据
        assert len(analysis_test_data['demands']) > 0
        
        # 准备请求数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        request_data = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'community_ids': None
        }
        
        response = client.post(
            '/api/reports/time-range',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'report_id' in data
        assert 'report_url' in data
    
    def test_time_range_report_api_with_community_filter(self, client, analysis_test_data):
        """测试时间范围报告API - 带社区筛选"""
        # 确保有测试数据
        assert len(analysis_test_data['communities']) > 0
        
        # 准备请求数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        request_data = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'community_ids': [analysis_test_data['communities'][0]]
        }
        
        response = client.post(
            '/api/reports/time-range',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_time_range_report_api_invalid_dates(self, client):
        """测试时间范围报告API - 无效日期"""
        # 测试缺少日期
        response = client.post(
            '/api/reports/time-range',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '日期' in data['message']
    
    def test_time_range_report_api_invalid_date_format(self, client):
        """测试时间范围报告API - 无效日期格式"""
        request_data = {
            'start_date': 'invalid-date',
            'end_date': 'invalid-date'
        }
        
        response = client.post(
            '/api/reports/time-range',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '格式' in data['message']


@pytest.fixture(scope='session')
def init_test_db():
    """初始化测试数据库 - 整个测试会话只执行一次"""
    from database.init_database import init_database
    init_database()
    yield
    # 清理代码可以放在这里


@pytest.fixture
def app(init_test_db):
    """创建测试应用"""
    import sys
    import os
    
    # 确保导入正确的 app 模块
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    
    # 禁用监控初始化以避免测试中的副作用
    flask_app.before_request_funcs = {}
    
    return flask_app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def sample_demand(db_session):
    """创建示例需求数据"""
    from database.db_manager import DatabaseManager
    from sqlalchemy import text
    
    db = DatabaseManager()
    community_id = None
    demand_id = None
    
    try:
        # 先创建社区
        with db.engine.begin() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO communities (name, source_type, status, config, created_at)
                    VALUES (:name, :source_type, :status, :config, :created_at)
                """),
                {
                    'name': '__TEST_Community__',
                    'source_type': 'reddit',
                    'status': 'active',
                    'config': '{}',
                    'created_at': datetime.now()
                }
            )
            community_id = result.lastrowid
        
        # 创建需求
        with db.engine.begin() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO demand_signals (
                        community_id, title, content, signal_type,
                        hotness_score, sentiment_score, source_url,
                        author, discussion_count, participant_count,
                        created_at
                    )
                    VALUES (
                        :community_id, :title, :content, :signal_type,
                        :hotness_score, :sentiment_score, :source_url,
                        :author, :discussion_count, :participant_count,
                        :created_at
                    )
                """),
                {
                    'community_id': community_id,
                    'title': '__TEST_Demand__',
                    'content': 'This is a test demand content',
                    'signal_type': 'pain_point',
                    'hotness_score': 85.5,
                    'sentiment_score': -0.3,
                    'source_url': 'https://reddit.com/r/test/comments/test123',  # 使用真实格式的 URL
                    'author': 'test_user',
                    'discussion_count': 10,
                    'participant_count': 5,
                    'created_at': datetime.now()
                }
            )
            demand_id = result.lastrowid
        
        # 返回一个简单的对象
        class Demand:
            def __init__(self, id, title, community_id):
                self.id = id
                self.title = title
                self.community_id = community_id
        
        yield Demand(demand_id, '__TEST_Demand__', community_id)
        
    finally:
        # 确保清理，即使测试失败
        try:
            with db.engine.begin() as conn:
                if demand_id:
                    conn.execute(text("DELETE FROM demand_signals WHERE id = :id"), {'id': demand_id})
                if community_id:
                    conn.execute(text("DELETE FROM communities WHERE id = :id"), {'id': community_id})
        except Exception as e:
            print(f"清理测试数据失败: {e}")
        finally:
            db.close()


@pytest.fixture
def db_session():
    """数据库会话 fixture"""
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    yield db
    db.close()


@pytest.fixture
def analysis_test_data(db_session):
    """为分析测试创建足够的测试数据"""
    from database.db_manager import DatabaseManager
    from sqlalchemy import text
    from datetime import datetime, timedelta
    
    db = DatabaseManager()
    created_ids = {'communities': [], 'demands': []}
    
    try:
        # 创建多个测试社区
        communities = [
            ('Analysis Test Community 1', 'reddit'),
            ('Analysis Test Community 2', 'github'),
            ('Analysis Test Community 3', 'hackernews')
        ]
        
        for name, source_type in communities:
            with db.engine.begin() as conn:
                result = conn.execute(
                    text("""
                        INSERT INTO communities (name, source_type, status, config, created_at)
                        VALUES (:name, :source_type, :status, :config, :created_at)
                    """),
                    {
                        'name': name,
                        'source_type': source_type,
                        'status': 'active',
                        'config': '{}',
                        'created_at': datetime.now()
                    }
                )
                created_ids['communities'].append(result.lastrowid)
        
        # 创建多个测试需求信号，分布在过去30天内
        signal_types = ['pain_point', 'feature_request', 'bug_report']
        base_date = datetime.now()
        
        for i in range(15):  # 创建15个需求信号
            days_ago = i * 2  # 分布在过去30天
            created_at = base_date - timedelta(days=days_ago)
            community_id = created_ids['communities'][i % len(created_ids['communities'])]
            signal_type = signal_types[i % len(signal_types)]
            
            with db.engine.begin() as conn:
                result = conn.execute(
                    text("""
                        INSERT INTO demand_signals (
                            community_id, title, content, signal_type,
                            hotness_score, sentiment_score, source_url,
                            author, discussion_count, participant_count,
                            created_at
                        )
                        VALUES (
                            :community_id, :title, :content, :signal_type,
                            :hotness_score, :sentiment_score, :source_url,
                            :author, :discussion_count, :participant_count,
                            :created_at
                        )
                    """),
                    {
                        'community_id': community_id,
                        'title': f'Analysis Test Demand {i+1}',
                        'content': f'Test content for analysis {i+1}',
                        'signal_type': signal_type,
                        'hotness_score': 50.0 + (i * 3),  # 递增的热度
                        'sentiment_score': -0.5 + (i * 0.1),  # 递增的情感分数
                        'source_url': f'https://example.com/test/{i+1}',
                        'author': f'test_user_{i+1}',
                        'discussion_count': 5 + i,
                        'participant_count': 2 + (i // 2),
                        'created_at': created_at
                    }
                )
                created_ids['demands'].append(result.lastrowid)
        
        yield created_ids
        
    finally:
        # 清理测试数据
        with db.engine.begin() as conn:
            for demand_id in created_ids['demands']:
                conn.execute(text("DELETE FROM demand_signals WHERE id = :id"), {'id': demand_id})
            for community_id in created_ids['communities']:
                conn.execute(text("DELETE FROM communities WHERE id = :id"), {'id': community_id})
        
        db.close()
