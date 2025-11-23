#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安全的日志记录工具

避免在后台线程和程序关闭时出现日志错误
"""

import threading
from loguru import logger


def safe_log(level: str, message: str):
    """
    安全的日志记录，避免在程序关闭时出错
    
    Args:
        level: 日志级别 (info/error/warning/debug)
        message: 日志消息
    """
    # 在监控线程中不记录日志，避免程序关闭时的错误
    thread_name = threading.current_thread().name
    if thread_name.startswith('monitor') or thread_name.startswith('Thread'):
        return
    
    try:
        if level == 'info':
            logger.info(message)
        elif level == 'error':
            logger.error(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'debug':
            logger.debug(message)
    except Exception:
        # 完全忽略所有日志错误
        pass


def safe_log_info(message: str):
    """安全的 INFO 日志"""
    safe_log('info', message)


def safe_log_error(message: str):
    """安全的 ERROR 日志"""
    safe_log('error', message)


def safe_log_warning(message: str):
    """安全的 WARNING 日志"""
    safe_log('warning', message)


def safe_log_debug(message: str):
    """安全的 DEBUG 日志"""
    safe_log('debug', message)
