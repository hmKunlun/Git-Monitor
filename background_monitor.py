#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控 - 后台监控服务
可在后台运行，不显示任何窗口，持续监控Git命令操作
"""

import os
import sys
import time
import threading
import datetime
import signal
import atexit
from pathlib import Path

# 导入监控器
from gitmonitor.utils import load_config, pretty_print, ensure_dir_exists
from gitmonitor.monitor import GitOperationMonitor

class BackgroundMonitor:
    """Git命令后台监控服务"""
    
    def __init__(self, config_path="config.json"):
        """初始化后台监控器"""
        # 加载配置
        self.config_path = config_path
        self.config = load_config(self.config_path)
        
        # 初始化监控器
        self.monitor = GitOperationMonitor(self.config)
        self.running = False
        self.monitor_thread = None
        
        # 注册退出处理函数
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理信号"""
        self.stop()
        sys.exit(0)
    
    def cleanup(self):
        """退出前清理"""
        self.stop()
    
    def start(self):
        """启动监控服务"""
        if self.running:
            pretty_print("监控服务已经在运行中", "warning")
            return
        
        self.running = True
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_thread_func, daemon=True)
        self.monitor_thread.start()
        
        # 记录日志
        log_path = self.config.get("log_file", "./logs/gitmonitor.log")
        ensure_dir_exists(os.path.dirname(log_path))
        
        with open(log_path, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] 后台监控服务已启动\n")
        
        pretty_print("Git命令后台监控服务已启动", "success")
    
    def _monitor_thread_func(self):
        """监控线程函数"""
        try:
            self.monitor.start()
            
            # 保持线程运行
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            pretty_print(f"监控线程出错: {e}", "error")
            self.running = False
    
    def stop(self):
        """停止监控服务"""
        if not self.running:
            return
            
        pretty_print("正在停止Git命令监控服务...", "info")
        self.running = False
        
        # 停止监控器
        if hasattr(self, 'monitor'):
            self.monitor.stop()
        
        # 记录日志
        log_path = self.config.get("log_file", "./logs/gitmonitor.log")
        ensure_dir_exists(os.path.dirname(log_path))
        
        with open(log_path, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] 后台监控服务已停止\n")
        
        pretty_print("Git命令监控服务已停止", "success")

def run_as_background_service():
    """作为后台服务运行"""
    monitor = BackgroundMonitor()
    monitor.start()
    
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()

if __name__ == "__main__":
    run_as_background_service() 