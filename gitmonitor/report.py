#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控 - 报告生成模块
支持生成日报、周报和月报，格式包括HTML和Markdown
"""

import os
import json
import datetime
from collections import Counter, defaultdict
from pathlib import Path
import markdown
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from jinja2 import Template

from gitmonitor.utils import pretty_print, ensure_dir_exists


# 配置matplotlib支持中文字体
def configure_matplotlib_fonts():
    """
    配置matplotlib支持中文字体
    根据不同操作系统配置适当的字体
    """
    import platform
    
    system = platform.system()
    
    # 设置字体
    if system == 'Windows':
        # Windows常见中文字体
        fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'NSimSun', 'FangSong', 'KaiTi']
    elif system == 'Darwin':  # macOS
        fonts = ['PingFang SC', 'Hiragino Sans GB', 'Heiti SC', 'STHeiti']
    else:  # Linux
        fonts = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Droid Sans Fallback']
    
    # 尝试设置支持中文的字体
    font_found = False
    for font in fonts:
        try:
            matplotlib.rcParams['font.family'] = [font]
            matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号
            pretty_print(f"使用中文字体: {font}", "info")
            font_found = True
            break
        except Exception:
            continue
    
    # 如果没有找到合适的字体，尝试使用系统默认字体
    if not font_found:
        try:
            matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Bitstream Vera Sans']
            pretty_print("未找到支持中文的字体，使用默认字体", "warning")
        except Exception as e:
            pretty_print(f"配置字体时出错: {e}", "error")

# 初始化时配置字体
configure_matplotlib_fonts()


class GitReportGenerator:
    """Git命令报告生成器"""
    
    def __init__(self, config):
        """
        初始化报告生成器
        
        Args:
            config (dict): 配置信息
        """
        self.config = config
        self.storage_path = config.get("storage_path", "./data")
        self.report_path = config.get("report_path", "./reports")
        
        # 确保报告目录存在
        ensure_dir_exists(self.report_path)
        
        # 报告日期格式
        self.date_format = "%Y-%m-%d"
        
        # 创建图表目录
        self.charts_dir = os.path.join(self.report_path, "charts")
        ensure_dir_exists(self.charts_dir)
        
        # 图表配置
        self.chart_theme = config.get("report", {}).get("chart_theme", "default")
        self._configure_chart_style()
    
    def _configure_chart_style(self):
        """配置图表样式"""
        try:
            # 设置主题样式
            plt.style.use('seaborn-v0_8' if self.chart_theme == "default" else self.chart_theme)
            
            # 提高图表分辨率
            plt.rcParams['figure.dpi'] = 120
            
            # 配置通用字体大小
            plt.rcParams['font.size'] = 12
            plt.rcParams['axes.titlesize'] = 14
            plt.rcParams['axes.labelsize'] = 12
            
        except Exception as e:
            pretty_print(f"配置图表样式时出错: {e}", "warning")
    
    def _load_data(self, start_date, end_date):
        """
        加载指定日期范围内的数据
        
        Args:
            start_date (datetime.date): 开始日期
            end_date (datetime.date): 结束日期
            
        Returns:
            list: 命令记录列表
        """
        records = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y%m%d")
            file_path = os.path.join(self.storage_path, f"{date_str}.json")
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        records.extend(data)
                except Exception as e:
                    pretty_print(f"加载数据文件 {file_path} 时出错: {e}", "error")
            
            # 移动到下一天
            current_date += datetime.timedelta(days=1)
        
        return records
    
    def _analyze_data(self, records):
        """
        分析Git命令数据
        
        Args:
            records (list): 命令记录列表
            
        Returns:
            dict: 分析结果
        """
        if not records:
            return {
                "total_commands": 0,
                "command_types": {},
                "hourly_distribution": {},
                "users": {},
                "repositories": {},
                "most_active_day": None,
                "daily_activity": {},
                "detailed_commits": []
            }
        
        # 命令类型统计
        command_types = Counter()
        for record in records:
            cmd = record["command"].split()[1] if len(record["command"].split()) > 1 else "unknown"
            command_types[cmd] += 1
        
        # 按小时分布
        hourly_distribution = defaultdict(int)
        for record in records:
            hour = datetime.datetime.fromisoformat(record["timestamp"]).hour
            hourly_distribution[hour] += 1
        
        # 用户统计
        users = Counter()
        for record in records:
            users[record["username"]] += 1
        
        # 仓库统计（根据工作目录）
        repositories = Counter()
        for record in records:
            # 尝试从工作目录获取仓库名称
            repo_path = record["working_directory"]
            repo_name = os.path.basename(repo_path)
            repositories[repo_name] += 1
        
        # 每日活动统计
        daily_activity = defaultdict(int)
        for record in records:
            day = datetime.datetime.fromisoformat(record["timestamp"]).strftime(self.date_format)
            daily_activity[day] += 1
        
        # 获取提交详情
        detailed_commits = []
        for record in records:
            if "analysis" in record and record["analysis"]["type"] == "commit":
                analysis = record["analysis"]
                commit_info = {
                    "timestamp": record["timestamp"],
                    "commit_hash": analysis.get("commit_hash", ""),
                    "author": analysis.get("author", ""),
                    "message": analysis.get("message", ""),
                    "files": analysis.get("files", []),
                    "stats": analysis.get("stats", {})
                }
                detailed_commits.append(commit_info)
        
        # 按时间排序提交详情（最新的在前）
        detailed_commits.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # 最活跃的日期
        most_active_day = max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else None
        
        return {
            "total_commands": len(records),
            "command_types": dict(command_types.most_common()),
            "hourly_distribution": dict(sorted(hourly_distribution.items())),
            "users": dict(users.most_common()),
            "repositories": dict(repositories.most_common(10)),  # 前10名仓库
            "most_active_day": most_active_day,
            "daily_activity": dict(sorted(daily_activity.items())),
            "detailed_commits": detailed_commits[:20]  # 最新的20个提交
        }
    
    def _generate_charts(self, analysis, period_name):
        """
        生成图表
        
        Args:
            analysis (dict): 分析结果
            period_name (str): 报告周期名称
            
        Returns:
            dict: 图表文件路径
        """
        charts = {}
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 确保matplotlib使用正确的中文字体
        configure_matplotlib_fonts()
        
        # 1. 命令类型分布图
        if analysis["command_types"]:
            plt.figure(figsize=(10, 6))
            cmd_types = dict(sorted(analysis["command_types"].items(), key=lambda x: x[1], reverse=True)[:10])
            plt.bar(cmd_types.keys(), cmd_types.values())
            plt.title('Git命令类型分布')
            plt.xlabel('命令类型')
            plt.ylabel('执行次数')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = os.path.join(self.charts_dir, f"cmd_types_{period_name}_{timestamp}.png")
            plt.savefig(chart_path, bbox_inches='tight', dpi=150)
            plt.close()
            charts["command_types"] = os.path.relpath(chart_path, self.report_path)
        
        # 2. 每小时分布图
        if analysis["hourly_distribution"]:
            plt.figure(figsize=(10, 6))
            hours = sorted(analysis["hourly_distribution"].keys())
            counts = [analysis["hourly_distribution"][h] for h in hours]
            plt.bar(hours, counts)
            plt.title('Git命令执行时间分布')
            plt.xlabel('小时')
            plt.ylabel('执行次数')
            plt.xticks(range(0, 24, 2))
            plt.tight_layout()
            
            chart_path = os.path.join(self.charts_dir, f"hourly_{period_name}_{timestamp}.png")
            plt.savefig(chart_path, bbox_inches='tight', dpi=150)
            plt.close()
            charts["hourly"] = os.path.relpath(chart_path, self.report_path)
        
        # 3. 每日活动图
        if analysis["daily_activity"]:
            plt.figure(figsize=(12, 6))
            days = list(analysis["daily_activity"].keys())
            counts = list(analysis["daily_activity"].values())
            plt.plot(days, counts, marker='o')
            plt.title('Git命令每日执行趋势')
            plt.xlabel('日期')
            plt.ylabel('执行次数')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = os.path.join(self.charts_dir, f"daily_{period_name}_{timestamp}.png")
            plt.savefig(chart_path, bbox_inches='tight', dpi=150)
            plt.close()
            charts["daily"] = os.path.relpath(chart_path, self.report_path)
        
        return charts
    
    def _generate_html(self, analysis, period_name, start_date, end_date, charts):
        """
        生成HTML报告
        
        Args:
            analysis (dict): 分析结果
            period_name (str): 报告周期名称
            start_date (datetime.date): 开始日期
            end_date (datetime.date): 结束日期
            charts (dict): 图表路径
            
        Returns:
            str: HTML报告文件路径
        """
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Git命令监控报告</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #2980b9;
                    margin-top: 30px;
                }
                h3 {
                    color: #3498db;
                    margin-top: 25px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }
                th, td {
                    text-align: left;
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr:hover {
                    background-color: #f5f5f5;
                }
                .chart {
                    margin: 30px 0;
                    text-align: center;
                }
                .chart img {
                    max-width: 100%;
                    height: auto;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .summary {
                    background-color: #f8f9fa;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
                }
                .footer {
                    margin-top: 50px;
                    text-align: center;
                    font-size: 0.8em;
                    color: #7f8c8d;
                }
                .commit {
                    background-color: #f9f9f9;
                    border: 1px solid #eee;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 20px;
                }
                .commit-header {
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    margin-bottom: 10px;
                }
                .commit-hash {
                    color: #e67e22;
                    font-family: monospace;
                }
                .commit-message {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .commit-details {
                    color: #7f8c8d;
                    font-size: 0.9em;
                }
                .file-changes {
                    margin-top: 10px;
                    font-size: 0.9em;
                }
                .file {
                    margin: 5px 0;
                }
                .added {
                    color: #27ae60;
                }
                .modified {
                    color: #f39c12;
                }
                .deleted {
                    color: #e74c3c;
                }
                .renamed {
                    color: #8e44ad;
                }
                .stats {
                    display: inline-block;
                    margin-left: 10px;
                    color: #7f8c8d;
                }
                .code {
                    background-color: #f0f0f0;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    font-family: monospace;
                    font-size: 0.9em;
                    padding: 10px;
                    overflow-x: auto;
                    white-space: pre;
                    margin-top: 5px;
                }
            </style>
        </head>
        <body>
            <h1>Git命令监控{{ period_name }}报告</h1>
            
            <div class="summary">
                <p><strong>报告周期:</strong> {{ start_date }} 至 {{ end_date }}</p>
                <p><strong>总命令数:</strong> {{ analysis.total_commands }}</p>
                {% if analysis.most_active_day %}
                <p><strong>最活跃日期:</strong> {{ analysis.most_active_day[0] }} ({{ analysis.most_active_day[1] }}条命令)</p>
                {% endif %}
            </div>
            
            <h2>命令类型分布</h2>
            {% if charts.command_types %}
            <div class="chart">
                <img src="{{ charts.command_types }}" alt="命令类型分布">
            </div>
            {% endif %}
            
            <table>
                <tr>
                    <th>命令类型</th>
                    <th>执行次数</th>
                    <th>占比</th>
                </tr>
                {% for cmd, count in analysis.command_types.items() %}
                <tr>
                    <td>{{ cmd }}</td>
                    <td>{{ count }}</td>
                    <td>{{ "%.2f"|format(count / analysis.total_commands * 100) }}%</td>
                </tr>
                {% endfor %}
            </table>
            
            <h2>时间分布</h2>
            {% if charts.hourly %}
            <div class="chart">
                <img src="{{ charts.hourly }}" alt="每小时分布">
            </div>
            {% endif %}
            
            <h2>每日活动</h2>
            {% if charts.daily %}
            <div class="chart">
                <img src="{{ charts.daily }}" alt="每日活动">
            </div>
            {% endif %}
            
            <h2>用户活跃度</h2>
            <table>
                <tr>
                    <th>用户</th>
                    <th>命令数</th>
                    <th>占比</th>
                </tr>
                {% for user, count in analysis.users.items() %}
                <tr>
                    <td>{{ user }}</td>
                    <td>{{ count }}</td>
                    <td>{{ "%.2f"|format(count / analysis.total_commands * 100) }}%</td>
                </tr>
                {% endfor %}
            </table>
            
            <h2>仓库活跃度</h2>
            <table>
                <tr>
                    <th>仓库</th>
                    <th>命令数</th>
                    <th>占比</th>
                </tr>
                {% for repo, count in analysis.repositories.items() %}
                <tr>
                    <td>{{ repo }}</td>
                    <td>{{ count }}</td>
                    <td>{{ "%.2f"|format(count / analysis.total_commands * 100) }}%</td>
                </tr>
                {% endfor %}
            </table>
            
            {% if analysis.detailed_commits %}
            <h2>最近提交记录</h2>
            {% for commit in analysis.detailed_commits %}
            <div class="commit">
                <div class="commit-header">
                    <div class="commit-message">{{ commit.message }}</div>
                    <div class="commit-details">
                        <span class="commit-hash">{{ commit.commit_hash[:8] }}</span> - 
                        {{ commit.author }} - 
                        {{ commit.timestamp.split("T")[0] }} {{ commit.timestamp.split("T")[1][:5] }}
                    </div>
                </div>
                
                <div class="file-changes">
                    <strong>变更文件 ({{ commit.files|length }}):</strong>
                    {% for file in commit.files %}
                    <div class="file">
                        <span class="{{ file.change_type }}">{{ file.change_type }}</span>: 
                        {{ file.filename }}
                        {% if file.diff %}
                        <div class="code">{{ file.diff }}</div>
                        {% endif %}
                    </div>
                    {% endfor %}
                    
                    {% if commit.stats %}
                    <div class="stats">
                        共 {{ commit.stats.files_changed }} 个文件, 
                        {{ commit.stats.insertions }} 次添加(+), 
                        {{ commit.stats.deletions }} 次删除(-)
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            {% endif %}
            
            <div class="footer">
                <p>生成时间: {{ now }}</p>
                <p>Git命令监控系统自动生成</p>
            </div>
        </body>
        </html>
        """
        
        # 渲染模板
        t = Template(template)
        html_content = t.render(
            analysis=analysis,
            period_name=period_name,
            start_date=start_date.strftime(self.date_format),
            end_date=end_date.strftime(self.date_format),
            charts=charts,
            now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 保存HTML文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"git_report_{period_name}_{start_date.strftime('%Y%m%d')}_{timestamp}.html"
        file_path = os.path.join(self.report_path, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path
    
    def _generate_markdown(self, analysis, period_name, start_date, end_date, charts):
        """
        生成Markdown报告
        
        Args:
            analysis (dict): 分析结果
            period_name (str): 报告周期名称
            start_date (datetime.date): 开始日期
            end_date (datetime.date): 结束日期
            charts (dict): 图表路径
            
        Returns:
            str: Markdown报告文件路径
        """
        # 构建Markdown内容
        md_content = f"""# Git命令监控{period_name}报告

## 报告概览

- **报告周期**: {start_date.strftime(self.date_format)} 至 {end_date.strftime(self.date_format)}
- **总命令数**: {analysis['total_commands']}
"""
        
        if analysis['most_active_day']:
            md_content += f"- **最活跃日期**: {analysis['most_active_day'][0]} ({analysis['most_active_day'][1]}条命令)\n"
        
        md_content += "\n## 命令类型分布\n\n"
        
        if charts.get('command_types'):
            md_content += f"![命令类型分布]({charts['command_types']})\n\n"
        
        md_content += "| 命令类型 | 执行次数 | 占比 |\n"
        md_content += "| -------- | -------- | ---- |\n"
        
        for cmd, count in analysis['command_types'].items():
            percentage = count / analysis['total_commands'] * 100 if analysis['total_commands'] > 0 else 0
            md_content += f"| {cmd} | {count} | {percentage:.2f}% |\n"
        
        md_content += "\n## 时间分布\n\n"
        
        if charts.get('hourly'):
            md_content += f"![每小时分布]({charts['hourly']})\n\n"
        
        md_content += "\n## 每日活动\n\n"
        
        if charts.get('daily'):
            md_content += f"![每日活动]({charts['daily']})\n\n"
        
        md_content += "\n## 用户活跃度\n\n"
        md_content += "| 用户 | 命令数 | 占比 |\n"
        md_content += "| ---- | ------ | ---- |\n"
        
        for user, count in analysis['users'].items():
            percentage = count / analysis['total_commands'] * 100 if analysis['total_commands'] > 0 else 0
            md_content += f"| {user} | {count} | {percentage:.2f}% |\n"
        
        md_content += "\n## 仓库活跃度\n\n"
        md_content += "| 仓库 | 命令数 | 占比 |\n"
        md_content += "| ---- | ------ | ---- |\n"
        
        for repo, count in analysis['repositories'].items():
            percentage = count / analysis['total_commands'] * 100 if analysis['total_commands'] > 0 else 0
            md_content += f"| {repo} | {count} | {percentage:.2f}% |\n"
        
        # 添加提交详情部分
        if analysis.get('detailed_commits'):
            md_content += "\n## 最近提交记录\n\n"
            
            for commit in analysis['detailed_commits']:
                # 提交标题和基本信息
                commit_time = commit['timestamp'].replace('T', ' ').split('.')[0]
                md_content += f"### {commit['message']}\n\n"
                md_content += f"**提交**: `{commit['commit_hash'][:8]}`  \n"
                md_content += f"**作者**: {commit['author']}  \n"
                md_content += f"**时间**: {commit_time}  \n\n"
                
                # 文件变更
                md_content += f"**变更文件 ({len(commit['files'])}):**\n\n"
                
                for file in commit['files']:
                    change_type_icon = ""
                    if file['change_type'] == 'added':
                        change_type_icon = "➕"
                    elif file['change_type'] == 'modified':
                        change_type_icon = "✏️"
                    elif file['change_type'] == 'deleted':
                        change_type_icon = "❌"
                    elif file['change_type'] == 'renamed':
                        change_type_icon = "🔄"
                    
                    md_content += f"- {change_type_icon} **{file['change_type']}**: `{file['filename']}`\n"
                    
                    # 如果有diff信息，添加代码块
                    if 'diff' in file:
                        md_content += "\n```\n"
                        md_content += file['diff']
                        md_content += "\n```\n"
                
                # 统计信息
                if commit.get('stats'):
                    stats = commit['stats']
                    md_content += f"\n**统计**: {stats.get('files_changed', 0)} 个文件, {stats.get('insertions', 0)} 次添加(+), {stats.get('deletions', 0)} 次删除(-)\n"
                
                md_content += "\n---\n\n"
        
        md_content += f"\n\n---\n生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \nGit命令监控系统自动生成"
        
        # 保存Markdown文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"git_report_{period_name}_{start_date.strftime('%Y%m%d')}_{timestamp}.md"
        file_path = os.path.join(self.report_path, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return file_path
    
    def generate_daily_report(self, target_date=None, format_type="both"):
        """
        生成日报
        
        Args:
            target_date (datetime.date, optional): 目标日期，默认为今天
            format_type (str): 报告格式，可选 'html', 'markdown', 'both'
            
        Returns:
            tuple: (html_path, md_path) 报告文件路径
        """
        if target_date is None:
            target_date = datetime.date.today()
        
        pretty_print(f"正在生成 {target_date.strftime(self.date_format)} 的日报...", "info")
        
        # 加载当日数据
        records = self._load_data(target_date, target_date)
        
        # 分析数据
        analysis = self._analyze_data(records)
        
        # 生成图表
        charts = self._generate_charts(analysis, "daily")
        
        # 生成报告
        html_path = None
        md_path = None
        
        if format_type in ["html", "both"]:
            html_path = self._generate_html(analysis, "日", target_date, target_date, charts)
            pretty_print(f"HTML日报已生成: {html_path}", "success")
        
        if format_type in ["markdown", "both"]:
            md_path = self._generate_markdown(analysis, "日", target_date, target_date, charts)
            pretty_print(f"Markdown日报已生成: {md_path}", "success")
        
        return html_path, md_path
    
    def generate_weekly_report(self, target_date=None, format_type="both"):
        """
        生成周报
        
        Args:
            target_date (datetime.date, optional): 目标日期，默认为今天
            format_type (str): 报告格式，可选 'html', 'markdown', 'both'
            
        Returns:
            tuple: (html_path, md_path) 报告文件路径
        """
        if target_date is None:
            target_date = datetime.date.today()
        
        # 计算本周开始日期（周一）
        start_of_week = target_date - datetime.timedelta(days=target_date.weekday())
        # 计算本周结束日期（周日）
        end_of_week = start_of_week + datetime.timedelta(days=6)
        
        pretty_print(f"正在生成 {start_of_week.strftime(self.date_format)} 至 {end_of_week.strftime(self.date_format)} 的周报...", "info")
        
        # 加载本周数据
        records = self._load_data(start_of_week, end_of_week)
        
        # 分析数据
        analysis = self._analyze_data(records)
        
        # 生成图表
        charts = self._generate_charts(analysis, "weekly")
        
        # 生成报告
        html_path = None
        md_path = None
        
        if format_type in ["html", "both"]:
            html_path = self._generate_html(analysis, "周", start_of_week, end_of_week, charts)
            pretty_print(f"HTML周报已生成: {html_path}", "success")
        
        if format_type in ["markdown", "both"]:
            md_path = self._generate_markdown(analysis, "周", start_of_week, end_of_week, charts)
            pretty_print(f"Markdown周报已生成: {md_path}", "success")
        
        return html_path, md_path
    
    def generate_monthly_report(self, target_date=None, format_type="both"):
        """
        生成月报
        
        Args:
            target_date (datetime.date, optional): 目标日期，默认为今天
            format_type (str): 报告格式，可选 'html', 'markdown', 'both'
            
        Returns:
            tuple: (html_path, md_path) 报告文件路径
        """
        if target_date is None:
            target_date = datetime.date.today()
        
        # 计算本月开始日期
        start_of_month = target_date.replace(day=1)
        
        # 计算本月结束日期
        if target_date.month == 12:
            end_of_month = target_date.replace(year=target_date.year + 1, month=1, day=1) - datetime.timedelta(days=1)
        else:
            end_of_month = target_date.replace(month=target_date.month + 1, day=1) - datetime.timedelta(days=1)
        
        pretty_print(f"正在生成 {start_of_month.strftime(self.date_format)} 至 {end_of_month.strftime(self.date_format)} 的月报...", "info")
        
        # 加载本月数据
        records = self._load_data(start_of_month, end_of_month)
        
        # 分析数据
        analysis = self._analyze_data(records)
        
        # 生成图表
        charts = self._generate_charts(analysis, "monthly")
        
        # 生成报告
        html_path = None
        md_path = None
        
        if format_type in ["html", "both"]:
            html_path = self._generate_html(analysis, "月", start_of_month, end_of_month, charts)
            pretty_print(f"HTML月报已生成: {html_path}", "success")
        
        if format_type in ["markdown", "both"]:
            md_path = self._generate_markdown(analysis, "月", start_of_month, end_of_month, charts)
            pretty_print(f"Markdown月报已生成: {md_path}", "success")
        
        return html_path, md_path 