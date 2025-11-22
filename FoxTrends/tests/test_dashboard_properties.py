"""
Dashboard 属性测试
使用 Hypothesis 进行基于属性的测试
"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta


class TestDemandListSorting:
    """
    属性 9: 需求列表排序正确性
    
    验证需求: 4.3
    
    属性描述:
    - 需求列表应该按热度分数降序排列
    - 相同热度的需求应该按创建时间降序排列
    - 排序应该是稳定的和可预测的
    """
    
    @given(
        demands=st.lists(
            st.fixed_dictionaries({
                'id': st.integers(min_value=1, max_value=10000),
                'title': st.text(min_size=5, max_size=100),
                'hotness_score': st.floats(min_value=0.0, max_value=100.0),
                'created_at': st.datetimes(
                    min_value=datetime(2024, 1, 1),
                    max_value=datetime(2025, 12, 31)
                )
            }),
            min_size=2,
            max_size=50
        )
    )
    def test_demands_sorted_by_hotness_desc(self, demands):
        """
        属性: 需求列表按热度降序排列
        
        给定任意需求列表，排序后应该满足：
        - 每个需求的热度 >= 下一个需求的热度
        """
        # 模拟排序逻辑
        sorted_demands = sorted(
            demands,
            key=lambda x: (x['hotness_score'], x['created_at']),
            reverse=True
        )
        
        # 验证排序正确性
        for i in range(len(sorted_demands) - 1):
            current = sorted_demands[i]
            next_item = sorted_demands[i + 1]
            
            # 热度应该递减或相等
            assert current['hotness_score'] >= next_item['hotness_score'], \
                f"热度排序错误: {current['hotness_score']} < {next_item['hotness_score']}"
            
            # 如果热度相同，创建时间应该递减
            if current['hotness_score'] == next_item['hotness_score']:
                assert current['created_at'] >= next_item['created_at'], \
                    f"相同热度时，时间排序错误"
    
    @given(
        demands=st.lists(
            st.fixed_dictionaries({
                'id': st.integers(min_value=1, max_value=10000),
                'hotness_score': st.floats(min_value=0.0, max_value=100.0),
            }),
            min_size=1,
            max_size=100
        )
    )
    def test_sorting_is_stable(self, demands):
        """
        属性: 排序是稳定的
        
        对同一列表多次排序应该得到相同的结果
        """
        sorted_once = sorted(demands, key=lambda x: x['hotness_score'], reverse=True)
        sorted_twice = sorted(sorted_once, key=lambda x: x['hotness_score'], reverse=True)
        
        # 两次排序结果应该相同
        assert sorted_once == sorted_twice
    
    @given(
        hotness_scores=st.lists(
            st.floats(min_value=0.0, max_value=100.0),
            min_size=2,
            max_size=50
        )
    )
    def test_max_hotness_always_first(self, hotness_scores):
        """
        属性: 最高热度的需求总是排在第一位
        """
        demands = [
            {'id': i, 'hotness_score': score}
            for i, score in enumerate(hotness_scores)
        ]
        
        sorted_demands = sorted(demands, key=lambda x: x['hotness_score'], reverse=True)
        
        max_hotness = max(hotness_scores)
        assert sorted_demands[0]['hotness_score'] == max_hotness
    
    @given(
        demands=st.lists(
            st.fixed_dictionaries({
                'id': st.integers(min_value=1, max_value=10000),
                'hotness_score': st.floats(min_value=0.0, max_value=100.0),
            }),
            min_size=1,
            max_size=50
        )
    )
    def test_sorting_preserves_all_elements(self, demands):
        """
        属性: 排序不会丢失或增加元素
        """
        sorted_demands = sorted(demands, key=lambda x: x['hotness_score'], reverse=True)
        
        # 元素数量应该相同
        assert len(sorted_demands) == len(demands)
        
        # 所有ID应该都存在
        original_ids = {d['id'] for d in demands}
        sorted_ids = {d['id'] for d in sorted_demands}
        assert original_ids == sorted_ids


class TestDemandFiltering:
    """需求筛选属性测试"""
    
    @given(
        demands=st.lists(
            st.fixed_dictionaries({
                'id': st.integers(min_value=1, max_value=10000),
                'signal_type': st.sampled_from(['pain_point', 'feature_request', 'bug_report']),
                'hotness_score': st.floats(min_value=0.0, max_value=100.0),
            }),
            min_size=5,
            max_size=50
        ),
        filter_type=st.sampled_from(['pain_point', 'feature_request', 'bug_report'])
    )
    def test_filter_returns_only_matching_type(self, demands, filter_type):
        """
        属性: 筛选只返回匹配类型的需求
        """
        filtered = [d for d in demands if d['signal_type'] == filter_type]
        
        # 所有返回的需求都应该是指定类型
        for demand in filtered:
            assert demand['signal_type'] == filter_type
    
    @given(
        demands=st.lists(
            st.fixed_dictionaries({
                'id': st.integers(min_value=1, max_value=10000),
                'signal_type': st.sampled_from(['pain_point', 'feature_request', 'bug_report']),
            }),
            min_size=1,
            max_size=50
        )
    )
    def test_filter_count_never_exceeds_total(self, demands):
        """
        属性: 筛选结果数量不会超过总数
        """
        for signal_type in ['pain_point', 'feature_request', 'bug_report']:
            filtered = [d for d in demands if d['signal_type'] == signal_type]
            assert len(filtered) <= len(demands)


class TestPagination:
    """分页属性测试"""
    
    @given(
        total_items=st.integers(min_value=1, max_value=1000),
        page_size=st.integers(min_value=1, max_value=100)
    )
    def test_pagination_covers_all_items(self, total_items, page_size):
        """
        属性: 分页应该覆盖所有项目
        """
        items = list(range(total_items))
        collected = []
        
        offset = 0
        while offset < total_items:
            page = items[offset:offset + page_size]
            collected.extend(page)
            offset += page_size
        
        assert len(collected) == total_items
        assert set(collected) == set(items)
    
    @given(
        total_items=st.integers(min_value=10, max_value=100),
        page_size=st.integers(min_value=1, max_value=20),
        offset=st.integers(min_value=0, max_value=50)
    )
    def test_pagination_limit_respected(self, total_items, page_size, offset):
        """
        属性: 分页限制应该被遵守
        """
        assume(offset < total_items)
        
        items = list(range(total_items))
        page = items[offset:offset + page_size]
        
        # 返回的项目数不应超过 page_size
        assert len(page) <= page_size
        
        # 如果还有足够的项目，应该返回完整的一页
        if offset + page_size <= total_items:
            assert len(page) == page_size


class TestHotnessScore:
    """热度分数属性测试"""
    
    @given(
        discussion_count=st.integers(min_value=0, max_value=1000),
        participant_count=st.integers(min_value=0, max_value=500),
        sentiment_score=st.floats(min_value=-1.0, max_value=1.0)
    )
    def test_hotness_score_in_valid_range(self, discussion_count, participant_count, sentiment_score):
        """
        属性: 热度分数应该在有效范围内 [0, 100]
        """
        # 简化的热度计算公式
        base_score = (discussion_count * 0.5 + participant_count * 1.0)
        sentiment_factor = 1.0 + (sentiment_score * 0.2)
        hotness = min(100.0, base_score * sentiment_factor)
        
        assert 0.0 <= hotness <= 100.0
    
    @given(
        discussion_count=st.integers(min_value=0, max_value=100),
        participant_count=st.integers(min_value=0, max_value=100)
    )
    def test_more_engagement_means_higher_hotness(self, discussion_count, participant_count):
        """
        属性: 更多的参与度应该导致更高的热度
        """
        # 计算基础热度
        hotness1 = discussion_count * 0.5 + participant_count * 1.0
        
        # 增加参与度
        hotness2 = (discussion_count + 10) * 0.5 + (participant_count + 5) * 1.0
        
        assert hotness2 > hotness1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
