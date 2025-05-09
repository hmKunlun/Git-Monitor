#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控工具 - 主入口文件
支持监控启动和报告生成
"""

import os
import sys
import time
import pyfiglet
import argparse
import datetime
from colorama import Fore, Style, init

from gitmonitor.utils import load_config, pretty_print, ensure_dir_exists
from gitmonitor.monitor import GitOperationMonitor
from gitmonitor.report import GitReportGenerator

# 初始化colorama
init()

def show_banner():
    """显示程序横幅"""
    banner = pyfiglet.figlet_format("Git Monitor", font="slant")
    print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}一个用于监控和分析Git操作的工具{Style.RESET_ALL}")
    print()

def start_monitoring(config):
    """启动监控功能"""
    # 确保数据目录存在
    storage_path = config.get("storage_path", "./data")
    ensure_dir_exists(storage_path)
    
    # 创建并启动监控器
    monitor = GitOperationMonitor(config)
    
    pretty_print("正在启动Git操作监控...", "info")
    monitor.start()
    
    # 保持运行，直到用户按Ctrl+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        pretty_print("Git命令监控已停止", "info")

def generate_report(config, report_type, target_date=None, format_type="both"):
    """生成报告"""
    if target_date is None:
        target_date = datetime.date.today()
    
    # 确保报告目录存在
    report_path = config.get("report_path", "./reports")
    ensure_dir_exists(report_path)
    
    # 创建报告生成器
    generator = GitReportGenerator(config)
    
    # 生成报告
    pretty_print(f"正在生成{report_type}报告...", "info")
    if report_type == "daily":
        html_path, md_path = generator.generate_daily_report(target_date, format_type)
    elif report_type == "weekly":
        html_path, md_path = generator.generate_weekly_report(target_date, format_type)
    elif report_type == "monthly":
        html_path, md_path = generator.generate_monthly_report(target_date, format_type)
    else:
        pretty_print(f"不支持的报告类型: {report_type}", "error")
        return
    
    pretty_print(f"报告生成完成！", "success")
    if html_path:
        pretty_print(f"HTML报告: {os.path.abspath(html_path)}", "info")
    if md_path:
        pretty_print(f"Markdown报告: {os.path.abspath(md_path)}", "info")

def parse_date(date_str):
    """解析日期字符串为日期对象"""
    if not date_str:
        return None
    
    try:
        # 尝试解析 YYYY-MM-DD 格式
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            # 尝试解析 YYYYMMDD 格式
            return datetime.datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            pretty_print(f"无效的日期格式: {date_str}，请使用YYYY-MM-DD或YYYYMMDD格式", "error")
            return None

def main():
    """主程序"""
    # 显示程序横幅
    show_banner()
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="Git命令监控工具")
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 监控命令
    monitor_parser = subparsers.add_parser("monitor", help="启动Git命令监控")
    
    # 报告命令
    report_parser = subparsers.add_parser("report", help="生成Git命令报告")
    report_parser.add_argument(
        "type",
        choices=["daily", "weekly", "monthly"],
        help="报告类型：daily(日报)、weekly(周报)、monthly(月报)"
    )
    report_parser.add_argument(
        "-d", "--date",
        help="报告日期，格式为YYYY-MM-DD或YYYYMMDD，默认为今天",
        default=None
    )
    report_parser.add_argument(
        "-f", "--format",
        choices=["html", "markdown", "both"],
        default="both",
        help="报告输出格式，默认同时生成HTML和Markdown"
    )
    
    # 所有命令通用参数
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="配置文件路径，默认为config.json"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = load_config(args.config)
        
        # 如果没有指定子命令，默认启动监控
        if not args.command or args.command == "monitor":
            start_monitoring(config)
        elif args.command == "report":
            target_date = parse_date(args.date)
            generate_report(config, args.type, target_date, args.format)
        
    except Exception as e:
        pretty_print(f"发生错误: {e}", "error")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 