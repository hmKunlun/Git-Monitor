#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git监控工具 - 工具函数模块
"""

import os
import json
import logging
from datetime import datetime
import socket
import getpass
from pathlib import Path
from colorama import Fore, Style, init

# 初始化colorama
init()

# 颜色常量
COLORS = {
    "info": Fore.BLUE,
    "success": Fore.GREEN,
    "warning": Fore.YELLOW,
    "error": Fore.RED,
    "debug": Fore.MAGENTA,
    "special": Fore.CYAN
}

def load_config(config_path="config.json"):
    """
    加载配置文件
    
    Args:
        config_path (str): 配置文件路径
        
    Returns:
        dict: 配置数据
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        pretty_print(f"配置文件 {config_path} 未找到，使用默认配置", "warning")
        return {
            "storage_path": "./data",
            "log_file": "./logs/monitor.log",
            "system_level_monitoring": True,
            "monitor_interval": 1,
            "ignored_commands": ["git status", "git diff"]
        }
    except json.JSONDecodeError:
        pretty_print(f"配置文件 {config_path} 格式错误，使用默认配置", "error")
        return {
            "storage_path": "./data", 
            "log_file": "./logs/monitor.log",
            "system_level_monitoring": True,
            "monitor_interval": 1,
            "ignored_commands": ["git status", "git diff"]
        }

def setup_logging(config):
    """
    设置日志记录
    
    Args:
        config (dict): 配置数据
    """
    log_file = config.get("log_file", "./logs/monitor.log")
    log_level = config.get("log_level", "INFO")
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    ensure_dir_exists(log_dir)
    
    # 设置日志级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    log_level = level_map.get(log_level.upper(), logging.INFO)
    
    # 配置日志
    logging.basicConfig(
        filename=log_file,
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 添加控制台处理器
    console = logging.StreamHandler()
    console.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def pretty_print(message, level="info"):
    """
    格式化输出消息
    
    Args:
        message (str): 消息内容
        level (str): 消息级别 (info, success, warning, error, debug, special)
    """
    color = COLORS.get(level, Fore.WHITE)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if level == "special":
        # 对special级别的消息进行特殊格式化
        formatted_message = format_special_output(message)
        print(f"{Fore.LIGHTBLACK_EX}[{timestamp}]{Style.RESET_ALL} {formatted_message}")
    else:
        print(f"{Fore.LIGHTBLACK_EX}[{timestamp}]{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")

def ensure_dir_exists(directory):
    """
    确保目录存在，不存在则创建
    
    Args:
        directory (str): 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        pretty_print(f"创建目录: {directory}", "info")

def get_system_info():
    """
    获取系统信息
    
    Returns:
        dict: 系统信息
    """
    return {
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "platform": os.name
    }

def save_command_record(command_data, storage_path="./data"):
    """
    保存命令记录到JSON文件
    
    Args:
        command_data (dict): 命令数据
        storage_path (str): 存储路径
    """
    ensure_dir_exists(storage_path)
    
    # 创建文件名 YYYYMMDD.json 格式
    date_str = datetime.now().strftime("%Y%m%d")
    file_path = os.path.join(storage_path, f"{date_str}.json")
    
    # 读取现有数据
    existing_data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            pretty_print(f"文件 {file_path} 格式错误，将重新创建", "warning")
    
    # 添加新数据
    existing_data.append(command_data)
    
    # 保存到文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
    pretty_print(f"已记录命令: {command_data['command']}", "success")

def is_ignored_command(command, ignored_list):
    """
    检查命令是否被忽略
    
    Args:
        command (str): 要检查的命令
        ignored_list (list): 忽略的命令列表
        
    Returns:
        bool: 是否忽略
    """
    return any(command.startswith(ignored_cmd) for ignored_cmd in ignored_list)

def get_git_command_description(command):
    """
    获取Git命令的描述
    """
    cmd_descriptions = {
        "git init": "初始化一个新的Git仓库",
        "git clone": "克隆远程仓库到本地",
        "git branch": "创建、列出或删除分支",
        "git checkout": "切换分支或恢复工作区文件",
        "git add": "将文件添加到暂存区",
        "git commit": "提交暂存区内容到本地仓库",
        "git merge": "合并分支",
        "git push": "推送本地分支到远程仓库",
        "git pull": "拉取远程分支并合并到本地",
        "git cherry-pick": "选择性地应用提交"
    }
    
    for cmd, desc in cmd_descriptions.items():
        if command.startswith(cmd):
            return desc
    
    return "Git命令"

def format_git_command(command):
    """
    格式化Git命令显示
    """
    parts = command.split()
    if len(parts) >= 2 and parts[0] == "git":
        return f"{Fore.CYAN}git {Fore.LIGHTCYAN_EX}{' '.join(parts[1:])}{Style.RESET_ALL}"
    return command

def get_repo_name_from_path(repo_path):
    """
    从仓库路径获取仓库名称
    """
    return os.path.basename(os.path.abspath(repo_path))

def parse_git_url(url):
    """
    解析Git URL，提取仓库名和所有者
    """
    if not url:
        return None, None
    
    # 处理SSH URL
    if url.startswith("git@"):
        parts = url.split(":")
        if len(parts) > 1:
            repo_parts = parts[1].split("/")
            if len(repo_parts) > 1:
                owner = repo_parts[-2]
                repo = repo_parts[-1]
                if repo.endswith(".git"):
                    repo = repo[:-4]
                return owner, repo
    
    # 处理HTTPS URL
    if url.startswith("http"):
        parts = url.split("/")
        if len(parts) > 3:
            owner = parts[-2]
            repo = parts[-1]
            if repo.endswith(".git"):
                repo = repo[:-4]
            return owner, repo
    
    return None, None

def save_github_record(github_record, storage_path="./data/github_records"):
    """
    将GitHub操作记录保存到特定文件中，便于查询和分析
    
    Args:
        github_record (str): 格式化的GitHub操作记录
        storage_path (str): 存储路径
    """
    if not github_record:
        return
        
    ensure_dir_exists(storage_path)
    
    # 创建文件名 github_records_YYYYMM.txt 格式
    date_str = datetime.now().strftime("%Y%m")
    file_path = os.path.join(storage_path, f"github_records_{date_str}.txt")
    
    # 追加记录到文件
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{github_record}\n")
        
    pretty_print(f"GitHub操作记录已保存", "success")

def format_special_output(text):
    """
    特殊格式输出，用于高亮显示GitHub操作记录
    
    Args:
        text (str): 要格式化的文本
        
    Returns:
        str: 格式化后的文本
    """
    # 检测是否包含GitHub链接
    if "@https://github.com/" in text:
        # 将GitHub链接部分高亮显示
        parts = text.split("@")
        time_part = parts[0]
        repo_part = parts[1].split("，")[0]
        message_part = "，".join(parts[1].split("，")[1:])
        
        return (f"{Fore.LIGHTBLACK_EX}{time_part}@{Style.RESET_ALL}"
                f"{Fore.LIGHTBLUE_EX}{repo_part}{Style.RESET_ALL}"
                f"{Fore.WHITE}，{message_part}{Style.RESET_ALL}")
    
    return text 