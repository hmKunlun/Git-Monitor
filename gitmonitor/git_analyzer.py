#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令内容分析模块
用于深入分析Git命令执行的变更内容
"""

import os
import re
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class GitCommandAnalyzer:
    """Git命令内容分析器"""
    
    def __init__(self):
        """初始化Git命令内容分析器"""
        self.logger = logging.getLogger(__name__)
        # 用于跟踪最近的commit信息，以便在push时关联
        self._last_commit_info = {}
    
    def analyze_command(self, command, working_directory):
        """
        分析Git命令并提取详细信息
        
        Args:
            command (str): Git命令
            working_directory (str): 工作目录
            
        Returns:
            dict: 命令分析结果
        """
        try:
            # 将命令分解为各部分
            parts = command.split()
            if len(parts) < 2 or parts[0] != "git":
                return None
            
            # 确定Git子命令
            subcommand = parts[1]
            
            # 根据不同的Git命令调用对应的分析方法
            if subcommand == "commit":
                result = self.analyze_commit(command, working_directory)
                # 存储最近的commit信息，用于在push时关联
                if result:
                    self._last_commit_info[working_directory] = {
                        "commit_hash": result.get("commit_hash"),
                        "message": result.get("message"),
                        "files": result.get("files", []),
                        "stats": result.get("stats", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                return result
            elif subcommand == "push":
                return self.analyze_push(command, working_directory)
            elif subcommand == "merge":
                return self.analyze_merge(command, working_directory)
            elif subcommand == "pull":
                return self.analyze_pull(command, working_directory)
            elif subcommand == "checkout":
                return self.analyze_checkout(command, working_directory)
            elif subcommand == "add":
                return self.analyze_add(command, working_directory)
            elif subcommand.startswith("remote"):
                return self.analyze_remote(command, working_directory)
            
            # 默认返回None
            return None
            
        except Exception as e:
            self.logger.error(f"分析Git命令时出错: {e}")
            return None
    
    def analyze_commit(self, command, working_directory):
        """
        分析git commit命令
        
        Args:
            command (str): Git命令
            working_directory (str): 工作目录
            
        Returns:
            dict: 提交分析结果
        """
        try:
            # 确保工作目录存在
            if not os.path.exists(working_directory):
                return None
            
            # 提取提交信息
            commit_msg = self._extract_commit_message(command)
            
            # 获取最近的提交
            result = self._run_git_command(["git", "log", "-1", "--name-status", "--pretty=format:%H|%an|%ae|%at|%s"], working_directory)
            if not result:
                return None
            
            # 解析提交信息
            lines = result.strip().split("\n")
            if not lines:
                return None
                
            # 第一行包含提交信息
            commit_info = lines[0].split("|")
            if len(commit_info) < 5:
                return None
            
            # 解析文件变更
            changed_files = []
            for i in range(1, len(lines)):
                if not lines[i].strip():
                    continue
                    
                # 解析变更类型和文件名
                change_parts = lines[i].split("\t")
                if len(change_parts) < 2:
                    continue
                    
                change_type = change_parts[0]
                filename = change_parts[1]
                
                # 映射Git变更类型代码
                change_type_map = {
                    "A": "added",
                    "M": "modified",
                    "D": "deleted",
                    "R": "renamed",
                    "C": "copied"
                }
                
                # 获取文件变更详情
                file_change = {
                    "filename": filename,
                    "change_type": change_type_map.get(change_type[0], "modified")
                }
                
                # 如果文件被添加或修改，获取diff信息
                if file_change["change_type"] in ["added", "modified"]:
                    file_diff = self._get_file_diff(commit_info[0], filename, working_directory)
                    if file_diff:
                        file_change["diff"] = file_diff
                
                changed_files.append(file_change)
            
            # 构建完整的提交分析结果
            commit_hash = commit_info[0]
            author_name = commit_info[1]
            author_email = commit_info[2]
            commit_time = int(commit_info[3])
            commit_msg_short = commit_info[4]
            
            # 计算统计信息
            stats = self._get_commit_stats(commit_hash, working_directory)
            
            return {
                "type": "commit",
                "commit_hash": commit_hash,
                "author": f"{author_name} <{author_email}>",
                "commit_date": datetime.fromtimestamp(commit_time).isoformat(),
                "message": commit_msg or commit_msg_short,
                "files": changed_files,
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"分析git commit命令时出错: {e}")
            return None
    
    def analyze_push(self, command, working_directory):
        """
        分析git push命令
        
        Args:
            command (str): Git命令
            working_directory (str): 工作目录
            
        Returns:
            dict: 推送分析结果
        """
        try:
            # 解析push命令参数
            parts = command.split()
            remote = "origin"
            branch = "master"
            
            # 提取远程仓库和分支
            args = parts[2:]
            if len(args) > 0 and not args[0].startswith("-"):
                remote = args[0]
            if len(args) > 1 and not args[1].startswith("-"):
                branch = args[1]
            
            # 获取远程仓库URL
            remote_url = self._get_remote_url(remote, working_directory)
            
            # 从远程URL中提取GitHub仓库链接
            github_repo = self._extract_github_repo(remote_url)
            
            # 获取本地分支和远程分支的差异
            pushed_commits = self._get_pushed_commits(remote, branch, working_directory)
            
            # 获取关联的commit信息
            last_commit = self._last_commit_info.get(working_directory, {})
            
            # 构建推送分析结果
            result = {
                "type": "push",
                "remote": remote,
                "remote_url": remote_url,
                "branch": branch,
                "commits": pushed_commits,
                "github_repo": github_repo,
                "associated_commit": last_commit if last_commit else None
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"分析git push命令时出错: {e}")
            return None
    
    def analyze_add(self, command, working_directory):
        """
        分析git add命令
        
        Args:
            command (str): Git命令
            working_directory (str): 工作目录
            
        Returns:
            dict: 添加分析结果
        """
        try:
            # 解析add命令参数
            parts = command.split()
            files = parts[2:] if len(parts) > 2 else ["."]
            
            # 获取添加到暂存区的文件列表
            added_files = []
            for file_pattern in files:
                # 如果是添加所有文件
                if file_pattern in [".", "-A", "--all"]:
                    # 获取所有添加的文件
                    result = self._run_git_command(["git", "status", "--porcelain"], working_directory)
                    if result:
                        for line in result.strip().split("\n"):
                            if not line.strip():
                                continue
                            status = line[:2].strip()
                            file_path = line[3:].strip()
                            if status in ["A", "M", "??"] and file_path:
                                added_files.append(file_path)
                else:
                    # 检查文件是否存在
                    file_path = os.path.join(working_directory, file_pattern)
                    if os.path.exists(file_path):
                        added_files.append(file_pattern)
            
            return {
                "type": "add",
                "files": added_files
            }
            
        except Exception as e:
            self.logger.error(f"分析git add命令时出错: {e}")
            return None
    
    def analyze_checkout(self, command, working_directory):
        """
        分析git checkout命令
        
        Args:
            command (str): Git命令
            working_directory (str): 工作目录
            
        Returns:
            dict: checkout分析结果
        """
        try:
            # 解析checkout命令参数
            parts = command.split()
            target = parts[2] if len(parts) > 2 else None
            create_branch = "-b" in parts
            
            # 判断是切换分支还是还原文件
            is_branch = True
            if target and os.path.exists(os.path.join(working_directory, target)):
                is_branch = False
            
            # 获取当前分支
            current_branch = self._get_current_branch(working_directory)
            
            return {
                "type": "checkout",
                "target": target,
                "is_branch": is_branch,
                "create_branch": create_branch,
                "previous_branch": current_branch
            }
            
        except Exception as e:
            self.logger.error(f"分析git checkout命令时出错: {e}")
            return None
    
    def analyze_merge(self, command, working_directory):
        """
        分析git merge命令
        
        Args:
            command (str): Git命令
            working_directory (str): 工作目录
            
        Returns:
            dict: 合并分析结果
        """
        try:
            # 解析merge命令参数
            parts = command.split()
            source_branch = parts[2] if len(parts) > 2 else None
            
            # 获取当前分支
            current_branch = self._get_current_branch(working_directory)
            
            # 检查合并冲突
            has_conflict = self._check_merge_conflict(working_directory)
            
            return {
                "type": "merge",
                "source_branch": source_branch,
                "target_branch": current_branch,
                "has_conflict": has_conflict
            }
            
        except Exception as e:
            self.logger.error(f"分析git merge命令时出错: {e}")
            return None
    
    def analyze_pull(self, command, working_directory):
        """
        分析git pull命令
        
        Args:
            command (str): Git命令
            working_directory (str): 工作目录
            
        Returns:
            dict: 拉取分析结果
        """
        try:
            # 解析pull命令参数
            parts = command.split()
            remote = "origin"
            branch = None
            
            args = parts[2:]
            if len(args) > 0 and not args[0].startswith("-"):
                remote = args[0]
            if len(args) > 1 and not args[1].startswith("-"):
                branch = args[1]
            
            # 获取当前分支
            current_branch = self._get_current_branch(working_directory)
            branch = branch or current_branch
            
            # 获取拉取前的提交哈希
            before_pull = self._get_current_commit_hash(working_directory)
            
            return {
                "type": "pull",
                "remote": remote,
                "branch": branch,
                "current_branch": current_branch,
                "before_pull_commit": before_pull
            }
            
        except Exception as e:
            self.logger.error(f"分析git pull命令时出错: {e}")
            return None
    
    def analyze_remote(self, command, working_directory):
        """
        分析git remote命令
        
        Args:
            command (str): Git命令
            working_directory (str): 工作目录
            
        Returns:
            dict: remote分析结果
        """
        try:
            parts = command.split()
            if len(parts) < 3:
                return {"type": "remote", "action": "list"}
            
            action = parts[2]
            if action == "add" and len(parts) >= 5:
                remote_name = parts[3]
                remote_url = parts[4]
                return {
                    "type": "remote",
                    "action": "add",
                    "name": remote_name,
                    "url": remote_url
                }
            elif action == "set-url" and len(parts) >= 5:
                remote_name = parts[3]
                remote_url = parts[4]
                return {
                    "type": "remote",
                    "action": "set-url",
                    "name": remote_name,
                    "url": remote_url
                }
            elif action == "remove" and len(parts) >= 4:
                remote_name = parts[3]
                return {
                    "type": "remote",
                    "action": "remove",
                    "name": remote_name
                }
            
            return {"type": "remote", "action": action}
            
        except Exception as e:
            self.logger.error(f"分析git remote命令时出错: {e}")
            return {"type": "remote", "action": "unknown"}
    
    def _extract_commit_message(self, command):
        """提取提交信息"""
        # 尝试从 -m "message" 格式提取
        m_match = re.search(r'-m\s+"([^"]*)"', command) or re.search(r"-m\s+'([^']*)'", command)
        if m_match:
            return m_match.group(1)
        
        # 尝试从 -m message 格式提取
        parts = command.split("-m")
        if len(parts) > 1:
            msg_part = parts[1].strip()
            # 如果消息部分不包含其他选项
            if not msg_part.startswith("-"):
                return msg_part
        
        return None
    
    def _run_git_command(self, cmd, cwd):
        """运行Git命令并返回输出"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.warning(f"Git命令执行失败: {' '.join(cmd)}, 错误: {result.stderr}")
                return None
        except Exception as e:
            self.logger.error(f"执行Git命令时出错: {e}")
            return None
    
    def _get_file_diff(self, commit_hash, filename, working_directory):
        """获取文件的diff信息"""
        try:
            # 先检查文件是否为二进制文件
            is_binary_cmd = ["git", "check-attr", "-a", filename]
            attr_result = self._run_git_command(is_binary_cmd, working_directory)
            
            # 如果文件是二进制文件，返回一个提示而不是内容
            if attr_result and ("binary: set" in attr_result or "diff: unset" in attr_result):
                return "[二进制文件，内容未显示]"
            
            # 获取文件diff
            try:
                cmd = ["git", "show", "--format=", f"{commit_hash}:{filename}"]
                result = self._run_git_command(cmd, working_directory)
                
                # 如果是二进制文件或结果为空，返回提示
                if result is None:
                    return "[文件内容未能获取]"
                    
                # 检查文件大小，如果太大只返回部分内容
                if len(result) > 2000:  # 限制大文件的显示内容
                    lines = result.split("\n")
                    return "\n".join(lines[:10]) + "\n...\n[文件太大，只显示前10行]"
                    
                # 返回diff的前10行（或更少）
                lines = result.split("\n")
                return "\n".join(lines[:min(10, len(lines))])
            except UnicodeDecodeError:
                # 处理编码错误
                return "[文件内容包含无法显示的字符]"
                
        except Exception as e:
            self.logger.debug(f"获取文件diff时出错: {e}")
            return "[获取文件内容时出错]"
    
    def _get_commit_stats(self, commit_hash, working_directory):
        """获取提交的统计信息"""
        try:
            cmd = ["git", "show", "--stat", "--format=", commit_hash]
            result = self._run_git_command(cmd, working_directory)
            if not result:
                return {}
                
            # 解析统计信息
            lines = result.strip().split("\n")
            last_line = lines[-1] if lines else ""
            
            # 提取插入和删除行数
            insertions = 0
            deletions = 0
            
            if "insertion" in last_line:
                insertions_match = re.search(r'(\d+) insertion', last_line)
                if insertions_match:
                    insertions = int(insertions_match.group(1))
            
            if "deletion" in last_line:
                deletions_match = re.search(r'(\d+) deletion', last_line)
                if deletions_match:
                    deletions = int(deletions_match.group(1))
            
            return {
                "files_changed": len(lines) - 1 if len(lines) > 1 else 0,
                "insertions": insertions,
                "deletions": deletions
            }
            
        except Exception as e:
            self.logger.error(f"获取提交统计信息时出错: {e}")
            return {}
    
    def _get_remote_url(self, remote, working_directory):
        """获取远程仓库URL"""
        try:
            cmd = ["git", "remote", "get-url", remote]
            return self._run_git_command(cmd, working_directory)
        except Exception as e:
            self.logger.error(f"获取远程仓库URL时出错: {e}")
            return None
    
    def _get_pushed_commits(self, remote, branch, working_directory):
        """获取推送的提交"""
        try:
            # 首先检查远程分支是否存在
            remote_exists_cmd = ["git", "ls-remote", "--heads", remote, branch]
            remote_exists = self._run_git_command(remote_exists_cmd, working_directory)
            
            # 如果远程分支不存在，可能是首次推送
            if not remote_exists:
                # 获取将要推送的本地提交
                local_commits_cmd = ["git", "log", "--pretty=format:%H|%an|%ae|%at|%s", branch]
                result = self._run_git_command(local_commits_cmd, working_directory)
            else:
                # 获取本地和远程分支的差异
                cmd = ["git", "log", f"{remote}/{branch}..{branch}", "--pretty=format:%H|%an|%ae|%at|%s"]
                result = self._run_git_command(cmd, working_directory)
            
            if not result or result.strip() == "":
                return []
                
            commits = []
            for line in result.strip().split("\n"):
                if not line.strip():
                    continue
                    
                parts = line.split("|")
                if len(parts) < 5:
                    continue
                    
                try:
                    commit_hash = parts[0]
                    author_name = parts[1]
                    author_email = parts[2]
                    commit_time = int(parts[3])
                    commit_msg = parts[4]
                    
                    # 获取提交的文件变更
                    files_cmd = ["git", "show", "--name-status", "--pretty=format:", commit_hash]
                    files_result = self._run_git_command(files_cmd, working_directory)
                    
                    changed_files = []
                    if files_result:
                        for file_line in files_result.strip().split("\n"):
                            if not file_line.strip():
                                continue
                                
                            file_parts = file_line.split("\t")
                            if len(file_parts) < 2:
                                continue
                                
                            change_type = file_parts[0]
                            filename = file_parts[1]
                            
                            # 映射Git变更类型代码
                            change_type_map = {
                                "A": "added",
                                "M": "modified",
                                "D": "deleted",
                                "R": "renamed",
                                "C": "copied"
                            }
                            
                            changed_files.append({
                                "filename": filename,
                                "change_type": change_type_map.get(change_type[0], "modified")
                            })
                    
                    # 获取统计信息
                    stats = self._get_commit_stats(commit_hash, working_directory)
                    
                    commits.append({
                        "commit_hash": commit_hash,
                        "author": f"{author_name} <{author_email}>",
                        "commit_date": datetime.fromtimestamp(commit_time).isoformat(),
                        "message": commit_msg,
                        "files": changed_files,
                        "stats": stats
                    })
                except Exception as e:
                    self.logger.warning(f"处理提交 {parts[0] if len(parts) > 0 else '未知'} 时出错: {e}")
                    # 跳过此提交，继续处理下一个
                    continue
            
            return commits
            
        except Exception as e:
            self.logger.error(f"获取推送的提交时出错: {e}")
            return []
    
    def _get_current_branch(self, working_directory):
        """获取当前分支名称"""
        try:
            cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
            return self._run_git_command(cmd, working_directory).strip()
        except Exception as e:
            self.logger.error(f"获取当前分支时出错: {e}")
            return None
    
    def _get_current_commit_hash(self, working_directory):
        """获取当前提交哈希"""
        try:
            cmd = ["git", "rev-parse", "HEAD"]
            return self._run_git_command(cmd, working_directory).strip()
        except Exception as e:
            self.logger.error(f"获取当前提交哈希时出错: {e}")
            return None
    
    def _check_merge_conflict(self, working_directory):
        """检查是否有合并冲突"""
        try:
            cmd = ["git", "status"]
            result = self._run_git_command(cmd, working_directory)
            return "Unmerged paths" in result if result else False
        except Exception as e:
            self.logger.error(f"检查合并冲突时出错: {e}")
            return False
    
    def _extract_github_repo(self, remote_url):
        """
        从远程URL中提取GitHub仓库链接
        
        Args:
            remote_url (str): 远程仓库URL
            
        Returns:
            str: GitHub仓库链接或None
        """
        if not remote_url:
            return None
            
        # 处理不同格式的GitHub URL
        github_patterns = [
            # HTTPS格式: https://github.com/user/repo.git
            r'https://github\.com/([^/]+)/([^/.]+)(?:\.git)?',
            # SSH格式: git@github.com:user/repo.git
            r'git@github\.com:([^/]+)/([^/.]+)(?:\.git)?'
        ]
        
        for pattern in github_patterns:
            match = re.search(pattern, remote_url)
            if match:
                user = match.group(1)
                repo = match.group(2)
                return f"https://github.com/{user}/{repo}"
                
        return None 