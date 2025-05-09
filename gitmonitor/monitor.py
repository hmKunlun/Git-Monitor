#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控核心模块
"""

import os
import sys
import time
import psutil
import threading
import logging
import json
from datetime import datetime
import socket
import getpass

from pynput import keyboard

from gitmonitor.utils import (
    pretty_print, ensure_dir_exists, get_system_info, 
    save_command_record, is_ignored_command, setup_logging, save_github_record
)
from gitmonitor.git_analyzer import GitCommandAnalyzer

class GitOperationMonitor:
    """Git操作监控器类"""
    
    def __init__(self, config):
        """
        初始化Git操作监控器
        
        Args:
            config (dict): 配置信息
        """
        self.config = config
        self.running = False
        self.monitor_thread = None
        self.storage_path = config.get("storage_path", "./data")
        self.monitor_interval = config.get("monitor_interval", 1)
        self.ignored_commands = config.get("ignored_commands", ["git status", "git diff"])
        
        # 添加已处理的进程ID集合，避免重复记录
        self.processed_pids = set()
        
        # 设置进程缓存过期时间（秒）
        self.pid_cache_ttl = config.get("pid_cache_ttl", 300)  # 默认5分钟
        self.last_cache_cleanup = time.time()
        
        # 创建Git命令分析器
        self.git_analyzer = GitCommandAnalyzer()
        
        # 确保存储目录存在
        ensure_dir_exists(self.storage_path)
        
        # 设置日志
        setup_logging(config)
        self.logger = logging.getLogger(__name__)
        
        # 系统信息
        self.system_info = get_system_info()
        
        pretty_print("Git操作监控器已初始化", "info")
    
    def _record_git_command(self, process):
        """
        记录Git命令
        
        Args:
            process (psutil.Process): 进程对象
        """
        try:
            # 获取进程ID
            pid = process.pid
            
            # 如果该进程已经处理过，跳过
            if pid in self.processed_pids:
                return
            
            # 获取命令行
            cmd_line = " ".join(process.cmdline())
            
            # 跳过忽略列表中的命令
            if is_ignored_command(cmd_line, self.ignored_commands):
                return
            
            # 获取工作目录
            working_directory = process.cwd()
            
            # 创建基本记录
            timestamp = datetime.now().isoformat()
            record = {
                "timestamp": timestamp,
                "command": cmd_line,
                "working_directory": working_directory,
                "username": process.username(),
                "hostname": self.system_info["hostname"],
                "pid": pid,
                "status": process.status()
            }
            
            # 分析Git命令内容
            try:
                analysis = self.git_analyzer.analyze_command(cmd_line, working_directory)
                if analysis:
                    record["analysis"] = analysis
                    
                    # 格式化GitHub相关操作记录
                    if self._should_format_github_record(analysis):
                        github_record = self._format_github_record(timestamp, analysis)
                        record["github_record"] = github_record
                        
                        # 保存GitHub记录到单独的文件中，便于查询
                        github_records_path = os.path.join(self.storage_path, "github_records")
                        save_github_record(github_record, github_records_path)
                    
                    # 添加人性化描述
                    if analysis["type"] == "commit":
                        files_changed = len(analysis.get("files", []))
                        stats = analysis.get("stats", {})
                        insertions = stats.get("insertions", 0)
                        deletions = stats.get("deletions", 0)
                        msg = analysis.get("message", "")
                        
                        description = f"提交了 {files_changed} 个文件 (+{insertions}/-{deletions}): {msg}"
                        record["description"] = description
                        
                    elif analysis["type"] == "push":
                        remote = analysis.get("remote", "origin")
                        branch = analysis.get("branch", "master")
                        commits = analysis.get("commits", [])
                        github_repo = analysis.get("github_repo")
                        associated_commit = analysis.get("associated_commit", {})
                        
                        description = f"推送 {len(commits)} 个提交到 {remote}/{branch}"
                        if github_repo:
                            description += f" ({github_repo})"
                        if associated_commit and associated_commit.get("message"):
                            description += f"\n最近提交: {associated_commit.get('message')}"
                        if commits:
                            file_changes = sum(len(commit.get("files", [])) for commit in commits)
                            description += f", 总计修改 {file_changes} 个文件"
                        
                        record["description"] = description
            except Exception as e:
                self.logger.error(f"分析Git命令内容时出错: {e}")
                # 即使分析失败，仍然继续记录基本命令信息
            
            # 保存记录
            save_command_record(record, self.storage_path)
            
            # 记录日志
            self.logger.info(f"记录Git命令: {cmd_line}")
            
            # 添加到已处理集合
            self.processed_pids.add(pid)
            
            # 输出更详细的信息
            if "github_record" in record:
                pretty_print(f"已记录命令: {cmd_line}", "success")
                pretty_print(f"GitHub操作: {record['github_record']}", "special")
            elif "description" in record:
                pretty_print(f"已记录命令: {cmd_line}", "success")
                pretty_print(f"执行操作: {record['description']}", "info")
            else:
                pretty_print(f"已记录命令: {cmd_line}", "success")
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            self.logger.warning(f"处理进程时出错: {e}")
        except Exception as e:
            self.logger.error(f"记录Git命令时发生错误: {e}")
            self.logger.exception("详细错误信息：")  # 记录完整的堆栈跟踪信息
    
    def _cleanup_pid_cache(self):
        """清理不再活跃的进程ID缓存"""
        # 获取当前所有活跃进程的PID
        current_time = time.time()
        
        # 每隔一段时间进行清理
        if current_time - self.last_cache_cleanup < 60:  # 每分钟最多清理一次
            return
            
        self.last_cache_cleanup = current_time
        
        try:
            active_pids = set()
            for proc in psutil.process_iter(['pid']):
                active_pids.add(proc.info['pid'])
            
            # 移除已经结束的进程ID
            expired_pids = self.processed_pids - active_pids
            if expired_pids:
                self.processed_pids -= expired_pids
                self.logger.debug(f"已清理 {len(expired_pids)} 个过期的进程缓存")
                
        except Exception as e:
            self.logger.error(f"清理进程缓存时出错: {e}")
    
    def _monitor_processes(self):
        """监控系统中的Git进程"""
        while self.running:
            try:
                # 遍历所有进程
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    # 检查是否是Git命令
                    if proc.info['cmdline'] and proc.info['cmdline'][0] == "git":
                        self._record_git_command(proc)
                
                # 定期清理进程缓存
                self._cleanup_pid_cache()
            
            except Exception as e:
                self.logger.error(f"监控进程时出错: {e}")
            
            # 暂停一段时间
            time.sleep(self.monitor_interval)
    
    def start(self):
        """启动监控"""
        if self.running:
            pretty_print("监控器已经在运行中", "warning")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_processes)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        pretty_print("Git操作监控已启动", "success")
        self.logger.info("Git操作监控已启动")
    
    def stop(self):
        """停止监控"""
        if not self.running:
            pretty_print("监控器未运行", "warning")
            return
        
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3.0)
        
        pretty_print("Git操作监控已停止", "info")
        self.logger.info("Git操作监控已停止")
    
    def status(self):
        """返回监控状态"""
        if self.running:
            return {
                "status": "running",
                "processed_pids": len(self.processed_pids),
                "storage_path": self.storage_path,
                "ignored_commands": self.ignored_commands
            }
        else:
            return {"status": "stopped"}

    def _should_format_github_record(self, analysis):
        """
        判断是否应该格式化GitHub记录
        
        Args:
            analysis (dict): 命令分析结果
            
        Returns:
            bool: 是否应格式化GitHub记录
        """
        if analysis["type"] == "push" and analysis.get("github_repo"):
            # 如果是push命令且有GitHub仓库链接
            return True
        return False

    def _format_github_record(self, timestamp, analysis):
        """
        格式化GitHub操作记录
        
        Args:
            timestamp (str): 时间戳
            analysis (dict): 命令分析结果
            
        Returns:
            str: 格式化的GitHub操作记录
        """
        if analysis["type"] != "push" or not analysis.get("github_repo"):
            return None
        
        # 格式化时间
        dt = datetime.fromisoformat(timestamp)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # 获取GitHub仓库链接
        github_repo = analysis.get("github_repo")
        
        # 获取关联的提交信息
        associated_commit = analysis.get("associated_commit", {})
        commit_message = associated_commit.get("message", "无提交信息")
        
        # 格式化记录
        github_record = f"{formatted_time} 修改了@{github_repo}，{commit_message}"
        
        return github_record

class KeyboardMonitor:
    """键盘监控器类，可用于未来扩展"""
    
    def __init__(self, config):
        """
        初始化键盘监控器
        
        Args:
            config (dict): 配置信息
        """
        self.config = config
        self.running = False
        self.listener = None
        self.logger = logging.getLogger(__name__)
    
    def _on_press(self, key):
        """按键按下事件处理"""
        try:
            # 这里可以添加特定按键组合的检测逻辑
            pass
        except Exception as e:
            self.logger.error(f"处理按键事件时出错: {e}")
    
    def start(self):
        """启动键盘监控"""
        if self.running:
            pretty_print("键盘监控器已经在运行中", "warning")
            return
        
        self.running = True
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()
        
        pretty_print("键盘监控已启动", "info")
    
    def stop(self):
        """停止键盘监控"""
        if not self.running:
            pretty_print("键盘监控器未运行", "warning")
            return
        
        self.running = False
        if self.listener:
            self.listener.stop()
        
        pretty_print("键盘监控已停止", "info") 