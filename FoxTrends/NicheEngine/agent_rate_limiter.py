#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent 速率限制器

控制 Agent API 调用的并发和速率，避免触发 Rate Limit
"""

import time
import threading
from queue import Queue, Empty
from typing import Callable, Any, Dict
from utils.safe_logger import safe_log_info, safe_log_warning, safe_log_error


class AgentRateLimiter:
    """
    Agent 速率限制器
    
    功能：
    - 控制并发调用数量
    - 限制调用速率（每分钟调用次数）
    - 队列化处理请求
    - 自动重试失败的请求
    """
    
    def __init__(self, 
                 max_concurrent: int = 2,
                 calls_per_minute: int = 10,
                 retry_on_rate_limit: bool = True):
        """
        初始化速率限制器
        
        Args:
            max_concurrent: 最大并发数
            calls_per_minute: 每分钟最大调用次数
            retry_on_rate_limit: 遇到 rate limit 时是否自动重试
        """
        self.max_concurrent = max_concurrent
        self.calls_per_minute = calls_per_minute
        self.retry_on_rate_limit = retry_on_rate_limit
        
        # 请求队列
        self.queue = Queue()
        
        # 并发控制
        self.semaphore = threading.Semaphore(max_concurrent)
        
        # 速率控制（记录最近的调用时间）
        self.call_times = []
        self.call_times_lock = threading.Lock()
        
        # 工作线程
        self.workers = []
        self.running = False
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'completed': 0,
            'failed': 0,
            'rate_limited': 0,
            'retried': 0
        }
        self.stats_lock = threading.Lock()
    
    def start(self, num_workers: int = 2):
        """启动工作线程"""
        if self.running:
            return
        
        self.running = True
        
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f'AgentWorker-{i}',
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        safe_log_info(f"AgentRateLimiter 已启动，{num_workers} 个工作线程")
    
    def stop(self):
        """停止工作线程"""
        self.running = False
        
        # 等待所有工作线程结束
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers.clear()
        safe_log_info("AgentRateLimiter 已停止")
    
    def submit(self, func: Callable, *args, **kwargs) -> None:
        """
        提交一个 Agent 调用请求
        
        Args:
            func: 要调用的函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        request = {
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'retry_count': 0
        }
        
        self.queue.put(request)
        
        with self.stats_lock:
            self.stats['total_requests'] += 1
    
    def _worker_loop(self):
        """工作线程主循环"""
        while self.running:
            try:
                # 从队列获取请求（超时1秒）
                request = self.queue.get(timeout=1)
                
                # 执行请求
                self._execute_request(request)
                
                self.queue.task_done()
                
            except Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                safe_log_error(f"Worker 异常: {e}")
    
    def _execute_request(self, request: Dict[str, Any]):
        """执行单个请求"""
        func = request['func']
        args = request['args']
        kwargs = request['kwargs']
        retry_count = request['retry_count']
        
        # 等待并发槽位
        self.semaphore.acquire()
        
        try:
            # 检查速率限制
            self._wait_for_rate_limit()
            
            # 记录调用时间
            with self.call_times_lock:
                self.call_times.append(time.time())
            
            # 执行函数
            func(*args, **kwargs)
            
            # 统计成功
            with self.stats_lock:
                self.stats['completed'] += 1
            
        except Exception as e:
            error_msg = str(e)
            
            # 检查是否是 rate limit 错误
            is_rate_limit = ('429' in error_msg or 
                           'rate limit' in error_msg.lower() or
                           'too many requests' in error_msg.lower())
            
            if is_rate_limit:
                with self.stats_lock:
                    self.stats['rate_limited'] += 1
                
                # 如果启用重试且未超过最大重试次数
                if self.retry_on_rate_limit and retry_count < 3:
                    safe_log_warning(f"遇到 rate limit，将在 {(retry_count + 1) * 10} 秒后重试")
                    
                    # 延迟后重新加入队列
                    time.sleep((retry_count + 1) * 10)
                    request['retry_count'] = retry_count + 1
                    self.queue.put(request)
                    
                    with self.stats_lock:
                        self.stats['retried'] += 1
                else:
                    safe_log_error(f"Agent 调用失败（rate limit，已达最大重试次数）: {error_msg}")
                    with self.stats_lock:
                        self.stats['failed'] += 1
            else:
                safe_log_error(f"Agent 调用失败: {error_msg}")
                with self.stats_lock:
                    self.stats['failed'] += 1
        
        finally:
            # 释放并发槽位
            self.semaphore.release()
    
    def _wait_for_rate_limit(self):
        """等待直到满足速率限制"""
        while True:
            with self.call_times_lock:
                # 清理60秒前的记录
                current_time = time.time()
                self.call_times = [t for t in self.call_times if current_time - t < 60]
                
                # 检查是否超过速率限制
                if len(self.call_times) < self.calls_per_minute:
                    return
            
            # 等待一段时间后重试
            time.sleep(1)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        with self.stats_lock:
            return self.stats.copy()
    
    def get_queue_size(self) -> int:
        """获取队列大小"""
        return self.queue.qsize()


# 全局单例
_global_limiter = None
_limiter_lock = threading.Lock()


def get_global_limiter() -> AgentRateLimiter:
    """获取全局速率限制器单例"""
    global _global_limiter
    
    if _global_limiter is None:
        with _limiter_lock:
            if _global_limiter is None:
                _global_limiter = AgentRateLimiter(
                    max_concurrent=2,  # 最多2个并发
                    calls_per_minute=10,  # 每分钟最多10次调用
                    retry_on_rate_limit=True
                )
                _global_limiter.start(num_workers=2)
    
    return _global_limiter
