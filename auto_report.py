#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控 - 自动报告生成脚本
可在Windows计划任务中定时执行
"""

import os
import sys
import time
import datetime
import logging
import traceback

from gitmonitor.utils import load_config, pretty_print, ensure_dir_exists, setup_logging
from gitmonitor.report import GitReportGenerator

def is_last_day_of_month(date):
    """判断是否为月末"""
    if date.month == 12:
        next_month = date.replace(year=date.year + 1, month=1, day=1)
    else:
        next_month = date.replace(month=date.month + 1, day=1)
    
    last_day = next_month - datetime.timedelta(days=1)
    return date.day == last_day.day

def is_sunday(date):
    """判断是否为周日"""
    return date.weekday() == 6

def main():
    """主程序"""
    try:
        # 加载配置
        config = load_config("config.json")
        
        # 设置日志
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        # 检查自动生成报告设置
        report_config = config.get("report", {})
        auto_generate = report_config.get("auto_generate", {})
        
        if not auto_generate.get("enabled", False):
            pretty_print("自动报告生成功能未启用，退出", "warning")
            return 0
        
        # 确保报告目录存在
        report_path = config.get("report_path", "./reports")
        ensure_dir_exists(report_path)
        
        # 获取当前日期
        today = datetime.date.today()
        
        # 创建报告生成器
        generator = GitReportGenerator(config)
        
        # 生成日报
        if auto_generate.get("daily", True):
            html_path, md_path = generator.generate_daily_report(today)
            logger.info(f"生成日报: HTML={html_path}, MD={md_path}")
        
        # 生成周报（周日）
        if auto_generate.get("weekly", True) and is_sunday(today):
            html_path, md_path = generator.generate_weekly_report(today)
            logger.info(f"生成周报: HTML={html_path}, MD={md_path}")
        
        # 生成月报（月末）
        if auto_generate.get("monthly", True) and is_last_day_of_month(today):
            html_path, md_path = generator.generate_monthly_report(today)
            logger.info(f"生成月报: HTML={html_path}, MD={md_path}")
        
        pretty_print("自动报告生成完成", "success")
        return 0
    
    except Exception as e:
        pretty_print(f"自动生成报告时出错: {e}", "error")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 