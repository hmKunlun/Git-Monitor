#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控 - 报告生成命令行工具
"""

import os
import sys
import argparse
import datetime
from colorama import Fore, Style, init

from gitmonitor.utils import load_config, pretty_print, ensure_dir_exists
from gitmonitor.report import GitReportGenerator

# 初始化colorama
init()

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
    parser = argparse.ArgumentParser(description="Git命令监控报告生成工具")
    
    # 添加报告类型参数
    parser.add_argument(
        "report_type",
        choices=["daily", "weekly", "monthly"],
        help="报告类型：daily(日报)、weekly(周报)、monthly(月报)"
    )
    
    # 添加日期参数
    parser.add_argument(
        "-d", "--date",
        help="报告日期，格式为YYYY-MM-DD或YYYYMMDD，默认为今天",
        default=None
    )
    
    # 添加输出格式参数
    parser.add_argument(
        "-f", "--format",
        choices=["html", "markdown", "both"],
        default="both",
        help="报告输出格式，默认同时生成HTML和Markdown"
    )
    
    # 添加配置文件参数
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="配置文件路径，默认为config.json"
    )
    
    # 添加输出路径参数
    parser.add_argument(
        "-o", "--output",
        help="报告输出目录，默认为配置文件中的report_path或./reports"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = load_config(args.config)
        
        # 设置输出目录
        if args.output:
            config["report_path"] = args.output
        
        # 确保输出目录存在
        report_path = config.get("report_path", "./reports")
        ensure_dir_exists(report_path)
        
        # 解析日期
        target_date = parse_date(args.date)
        if target_date is None:
            target_date = datetime.date.today()
        
        # 创建报告生成器
        generator = GitReportGenerator(config)
        
        # 根据报告类型生成报告
        if args.report_type == "daily":
            html_path, md_path = generator.generate_daily_report(target_date, args.format)
        elif args.report_type == "weekly":
            html_path, md_path = generator.generate_weekly_report(target_date, args.format)
        elif args.report_type == "monthly":
            html_path, md_path = generator.generate_monthly_report(target_date, args.format)
        
        # 显示结果
        pretty_print(f"报告生成完成！", "success")
        if html_path:
            pretty_print(f"HTML报告: {os.path.abspath(html_path)}", "info")
        if md_path:
            pretty_print(f"Markdown报告: {os.path.abspath(md_path)}", "info")
        
        return 0
    
    except Exception as e:
        pretty_print(f"生成报告时出错: {e}", "error")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 