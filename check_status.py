#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控器状态检查工具
"""

import sys
import json
from colorama import Fore, Style, init
from gitmonitor.utils import load_config, pretty_print
from gitmonitor.monitor import GitOperationMonitor

# 初始化colorama
init()

def main():
    """主程序"""
    try:
        # 加载配置
        config = load_config("config.json")
        
        # 创建监控器实例（不启动）
        monitor = GitOperationMonitor(config)
        
        # 显示配置信息
        pretty_print("Git命令监控器配置信息：", "info")
        print(f"{Fore.CYAN}存储路径：{Fore.WHITE}{config.get('storage_path', './data')}")
        print(f"{Fore.CYAN}监控间隔：{Fore.WHITE}{config.get('monitor_interval', 1)}秒")
        
        # 显示忽略的命令
        ignored_commands = config.get("ignored_commands", [])
        if ignored_commands:
            pretty_print("当前被忽略的Git命令：", "warning")
            for cmd in ignored_commands:
                print(f"{Fore.YELLOW} - {cmd}{Style.RESET_ALL}")
        else:
            pretty_print("没有设置忽略的Git命令", "success")
        
        # 显示其他配置信息
        pid_cache_ttl = config.get("pid_cache_ttl", 300)
        pretty_print(f"进程缓存时间：{pid_cache_ttl}秒", "info")
        
        return 0
    except Exception as e:
        pretty_print(f"检查状态时出错: {e}", "error")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 