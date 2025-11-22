"""
Dashboard API 端点测试
"""
import pytest
from datetime import datetime


class TestDashboardAPI:
    """Dashboard API 测试类"""
    
    def test_list_communities(self, client):
        """测试获取社区列表"""
        response = client.get('/api/communities')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'communities' in data
        assert isinstance(data['communities'], list)
    
    def test_add_community(self, client):
        """测试添加社区"""
        community_data = {
            'name': 'Test Reddit',
            'source_type': 'reddit',
            'config': {'subreddit': 'python'}
        }
        
        response = client.post(
            '/api/communities',
            json=community_data
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'community' in data
        assert data['community']['name'] == 'Test Reddit'
    
    def test_add_community_missing_params(self, client):
        """测试添加社区缺少参数"""
        response = client.post(
            '/api/communities',
            json={'name': 'Test'}
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_list_demands(self, client):
        """测试获取需求列表"""
        response = client.get('/api/demands')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'demands' in data
        assert isinstance(data['demands'], list)
        assert 'total' in data
    
    def test_list_demands_with_filter(self, client):
        """测试带筛选的需求列表"""
        response = client.get('/api/demands?signal_type=pain_point&limit=10')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['limit'] == 10
    
    def test_get_demand_detail(self, client, sample_demand):
        """测试获取需求详情"""
        response = client.get(f'/api/demands/{sample_demand.id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'demand' in data
        assert data['demand']['id'] == sample_demand.id
        assert data['demand']['title'] == sample_demand.title
    
    def test_get_demand_detail_not_found(self, client):
        """测试获取不存在的需求"""
        response = client.get('/api/demands/99999')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_get_dashboard_stats(self, client):
        """测试获取统计数据"""
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
        
        # 验证数据类型
        assert isinstance(stats['total_communities'], int)
        assert isinstance(stats['avg_hotness'], (int, float))
    
    def test_generate_report(self, client, sample_demand):
        """测试生成报告"""
        report_data = {
            'demand_ids': [sample_demand.id],
            'report_type': 'demand_analysis'
        }
        
        response = client.post(
            '/api/reports/generate',
            json=report_data
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'report_id' in data
    
    def test_generate_report_no_demands(self, client):
        """测试生成报告但未选择需求"""
        response = client.post(
            '/api/reports/generate',
            json={'demand_ids': []}
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False


@pytest.fixture
def sample_demand(db_session):
    """创建示例需求数据"""
    from database.db_manager import DatabaseManager
    
    db = DatabaseManager()
    
    # 先创建社区
    community_query = """
        INSERT INTO communities (name, source_type, status, config, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    community_result = db.execute_query(
        community_query,
        ('Test Community', 'reddit', 'active', '{}', datetime.now())
    )
    community_id = community_result[0][0]
    
    # 创建需求
    demand_query = """
        INSERT INTO demand_signals (
            community_id, title, content, signal_type,
            hotness_score, sentiment_score, source_url,
            author, discussion_count, participant_count,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    demand_result = db.execute_query(
        demand_query,
        (
            community_id,
            'Test Demand',
            'This is a test demand content',
            'pain_point',
            85.5,
            -0.3,
            'https://example.com/test',
            'test_user',
            10,
            5,
            datetime.now()
        )
    )
    demand_id = demand_result[0][0]
    
    # 返回一个简单的对象
    class Demand:
        def __init__(self, id, title):
            self.id = id
            self.title = title
    
    yield Demand(demand_id, 'Test Demand')
    
    # 清理
    db.execute_query("DELETE FROM demand_signals WHERE id = %s", (demand_id,))
    db.execute_query("DELETE FROM communities WHERE id = %s", (community_id,))


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def app():
    """创建测试应用"""
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    return flask_app
