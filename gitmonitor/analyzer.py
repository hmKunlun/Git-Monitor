"""
Git提交和修改分析模块，用于分析Git仓库中的提交和文件修改
"""
import os
import re
import logging
import git
from datetime import datetime, timedelta
from tabulate import tabulate
from colorama import Fore, Style
from gitmonitor.utils import pretty_print

logger = logging.getLogger(__name__)

class GitAnalyzer:
    """Git分析器类"""
    
    def __init__(self, config=None):
        """初始化Git分析器"""
        if config is None:
            config = {}
        
        self.ui_config = config.get("ui", {})
        self.date_format = self.ui_config.get("date_format", "%Y-%m-%d %H:%M:%S")
    
    def analyze_command(self, command_data):
        """
        分析Git命令，生成人类可读的摘要
        
        Args:
            command_data (dict): Git命令解析数据
            
        Returns:
            str: 命令摘要
        """
        if not command_data or "type" not in command_data:
            return "未知Git操作"
        
        cmd_type = command_data["type"]
        parsed_args = command_data.get("parsed_args", {})
        
        analyze_method = getattr(self, f"_analyze_{cmd_type}", None)
        if analyze_method:
            return analyze_method(parsed_args)
        
        return f"执行了 {command_data['command']}"
    
    def _analyze_init(self, args):
        """分析git init命令"""
        directory = args.get("directory", "当前目录")
        is_bare = args.get("is_bare", False)
        
        repo_type = "裸仓库" if is_bare else "仓库"
        return f"在 {directory} 初始化了一个新的Git{repo_type}"
    
    def _analyze_clone(self, args):
        """分析git clone命令"""
        repo_url = args.get("repository_url", "未知仓库")
        destination = args.get("destination", "当前目录")
        branch = args.get("branch")
        depth = args.get("depth")
        
        summary = f"从 {repo_url} 克隆仓库到 {destination}"
        if branch:
            summary += f"，指定分支: {branch}"
        if depth:
            summary += f"，浅克隆深度: {depth}"
        
        return summary
    
    def _analyze_branch(self, args):
        """分析git branch命令"""
        is_list = args.get("is_list", False)
        is_delete = args.get("is_delete", False)
        branch_name = args.get("branch_name")
        
        if is_list:
            return "列出了所有分支"
        elif is_delete and branch_name:
            return f"删除了分支 {branch_name}"
        elif branch_name:
            return f"创建了新分支 {branch_name}"
        
        return "执行了分支操作"
    
    def _analyze_checkout(self, args):
        """分析git checkout命令"""
        branch_name = args.get("branch_name")
        create_new = args.get("create_new", False)
        is_file = args.get("is_file", False)
        
        if not branch_name:
            return "检出操作"
        
        if is_file:
            return f"从暂存区还原文件 {branch_name}"
        elif create_new:
            return f"创建并切换到新分支 {branch_name}"
        else:
            return f"切换到分支 {branch_name}"
    
    def _analyze_add(self, args):
        """分析git add命令"""
        files = args.get("files", [])
        all_files = args.get("all", False)
        
        if all_files:
            return "添加所有修改文件到暂存区"
        elif files:
            if len(files) == 1:
                return f"添加文件 {files[0]} 到暂存区"
            else:
                return f"添加 {len(files)} 个文件到暂存区: {', '.join(files[:3])}{'...' if len(files) > 3 else ''}"
        
        return "添加文件到暂存区"
    
    def _analyze_commit(self, args):
        """分析git commit命令"""
        message = args.get("message", "")
        amend = args.get("amend", False)
        all_files = args.get("all", False)
        
        if amend:
            base = "修改了上一次提交"
        else:
            base = "提交了修改"
        
        if all_files:
            base += "（包括未暂存的文件）"
        
        if message:
            # 限制消息长度
            short_message = message[:50] + "..." if len(message) > 50 else message
            return f"{base}，提交信息: \"{short_message}\""
        
        return base
    
    def _analyze_merge(self, args):
        """分析git merge命令"""
        branch_name = args.get("branch_name")
        no_ff = args.get("no_ff", False)
        ff_only = args.get("ff_only", False)
        squash = args.get("squash", False)
        
        if not branch_name:
            return "执行了合并操作"
        
        result = f"将分支 {branch_name} 合并到当前分支"
        
        if squash:
            result += "（压缩提交）"
        elif no_ff:
            result += "（禁用快进）"
        elif ff_only:
            result += "（仅快进）"
        
        return result
    
    def _analyze_push(self, args):
        """分析git push命令"""
        remote = args.get("remote", "origin")
        branch = args.get("branch")
        force = args.get("force", False)
        all_branches = args.get("all", False)
        
        result = f"推送到远程 {remote}"
        
        if all_branches:
            result += " 的所有分支"
        elif branch:
            result += f" 的 {branch} 分支"
        
        if force:
            result += "（强制推送）"
        
        return result
    
    def _analyze_pull(self, args):
        """分析git pull命令"""
        remote = args.get("remote", "origin")
        branch = args.get("branch")
        rebase = args.get("rebase", False)
        
        result = f"从远程 {remote} 拉取"
        
        if branch:
            result += f" {branch} 分支"
        
        if rebase:
            result += "（使用变基）"
        else:
            result += "（使用合并）"
        
        return result
    
    def _analyze_cherry_pick(self, args):
        """分析git cherry-pick命令"""
        commit_hash = args.get("commit_hash")
        no_commit = args.get("no_commit", False)
        edit = args.get("edit", False)
        continue_op = args.get("continue", False)
        
        if continue_op:
            return "继续进行中的cherry-pick操作"
        
        if not commit_hash:
            return "执行了cherry-pick操作"
        
        result = f"选择性应用提交 {commit_hash}"
        
        if no_commit:
            result += "（不自动提交）"
        if edit:
            result += "（编辑提交信息）"
        
        return result
    
    def summarize_recent_activities(self, commands, limit=10):
        """
        总结最近的Git活动
        
        Args:
            commands (list): Git命令记录列表
            limit (int): 限制记录数量
            
        Returns:
            str: 活动总结
        """
        if not commands:
            return "没有找到最近的Git活动记录"
        
        # 按照仓库分组
        repos = {}
        for cmd in commands[:limit]:
            repo = cmd.get("repository", "未知仓库")
            if repo not in repos:
                repos[repo] = []
            repos[repo].append(cmd)
        
        summary = []
        for repo, repo_commands in repos.items():
            summary.append(f"\n{Fore.BLUE}仓库: {Style.BRIGHT}{repo}{Style.RESET_ALL}")
            
            table_data = []
            for cmd in repo_commands:
                cmd_time = datetime.strptime(cmd["timestamp"], "%Y-%m-%d %H:%M:%S") if isinstance(cmd["timestamp"], str) else cmd["timestamp"]
                cmd_time_str = cmd_time.strftime(self.date_format)
                
                table_data.append([
                    cmd_time_str,
                    cmd["command"][:50] + "..." if len(cmd["command"]) > 50 else cmd["command"],
                    cmd.get("description", "")
                ])
            
            table = tabulate(
                table_data,
                headers=["时间", "命令", "描述"],
                tablefmt="simple"
            )
            summary.append(table)
        
        return "\n".join(summary)
    
    def analyze_commit_details(self, commit_data):
        """
        分析提交详情
        
        Args:
            commit_data (dict): 提交数据
            
        Returns:
            str: 提交详情分析
        """
        if not commit_data:
            return "没有提交数据"
        
        # 提取基本信息
        commit_hash = commit_data.get("commit_hash", "未知")
        short_hash = commit_hash[:7] if len(commit_hash) > 7 else commit_hash
        author = commit_data.get("author", "未知")
        commit_date = commit_data.get("commit_date")
        if isinstance(commit_date, str):
            try:
                commit_date = datetime.strptime(commit_date, "%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        message = commit_data.get("message", "").strip()
        files_changed = commit_data.get("files_changed", 0)
        insertions = commit_data.get("insertions", 0)
        deletions = commit_data.get("deletions", 0)
        
        # 格式化日期
        date_str = commit_date.strftime(self.date_format) if isinstance(commit_date, datetime) else str(commit_date)
        
        # 构建提交详情
        details = [
            f"{Fore.YELLOW}提交: {Style.BRIGHT}{short_hash}{Style.RESET_ALL}",
            f"{Fore.CYAN}作者: {Style.RESET_ALL}{author}",
            f"{Fore.CYAN}日期: {Style.RESET_ALL}{date_str}",
            f"{Fore.CYAN}文件变更: {Style.RESET_ALL}{files_changed} 个文件 ({Fore.GREEN}+{insertions}{Style.RESET_ALL}, {Fore.RED}-{deletions}{Style.RESET_ALL})",
            f"{Fore.CYAN}提交信息: {Style.RESET_ALL}\n{message}"
        ]
        
        # 添加文件变更详情
        if "file_changes" in commit_data and commit_data["file_changes"]:
            details.append(f"\n{Fore.YELLOW}文件变更详情:{Style.RESET_ALL}")
            
            table_data = []
            for file_change in commit_data["file_changes"]:
                filename = file_change.get("filename", "")
                change_type = file_change.get("change_type", "modified")
                insertions = file_change.get("insertions", 0)
                deletions = file_change.get("deletions", 0)
                
                # 格式化变更类型
                type_color = Fore.YELLOW
                if change_type == "added":
                    type_color = Fore.GREEN
                elif change_type == "deleted":
                    type_color = Fore.RED
                
                type_str = f"{type_color}{change_type}{Style.RESET_ALL}"
                stats_str = f"{Fore.GREEN}+{insertions}{Style.RESET_ALL}, {Fore.RED}-{deletions}{Style.RESET_ALL}"
                
                table_data.append([filename, type_str, stats_str])
            
            table = tabulate(
                table_data,
                headers=["文件", "变更类型", "统计"],
                tablefmt="simple"
            )
            details.append(table)
        
        return "\n".join(details)
    
    def generate_repository_report(self, repo_path, days=7):
        """
        生成仓库报告
        
        Args:
            repo_path (str): 仓库路径
            days (int): 统计天数
            
        Returns:
            dict: 仓库报告数据
        """
        try:
            repo = git.Repo(repo_path)
            
            # 基本信息
            report = {
                "name": os.path.basename(os.path.abspath(repo_path)),
                "path": repo_path,
                "current_branch": repo.active_branch.name,
                "branches": [b.name for b in repo.branches],
                "remote_count": len(repo.remotes),
                "remotes": {r.name: r.url for r in repo.remotes},
                "commit_counts": {},
                "recent_commits": [],
                "contributors": {},
                "file_stats": {"total": 0, "types": {}}
            }
            
            # 获取提交统计
            since_date = datetime.now() - timedelta(days=days)
            commits = list(repo.iter_commits(since=since_date))
            
            report["commit_counts"] = {
                "total": len(list(repo.iter_commits())),
                "recent": len(commits)
            }
            
            # 分析最近的提交
            for commit in commits[:10]:  # 最多10个
                author_name = commit.author.name
                if author_name not in report["contributors"]:
                    report["contributors"][author_name] = {
                        "commits": 0,
                        "insertions": 0,
                        "deletions": 0
                    }
                
                # 提交统计
                stats = commit.stats.total
                report["contributors"][author_name]["commits"] += 1
                report["contributors"][author_name]["insertions"] += stats["insertions"]
                report["contributors"][author_name]["deletions"] += stats["deletions"]
                
                # 记录提交
                report["recent_commits"].append({
                    "hash": commit.hexsha,
                    "short_hash": commit.hexsha[:7],
                    "author": commit.author.name,
                    "date": datetime.fromtimestamp(commit.committed_date),
                    "message": commit.message.strip().split("\n")[0],  # 仅第一行
                    "stats": stats
                })
            
            # 文件统计
            try:
                for item in repo.tree().traverse():
                    if item.type == "blob":  # 是文件
                        report["file_stats"]["total"] += 1
                        
                        # 获取文件扩展名
                        _, ext = os.path.splitext(item.path)
                        if ext:
                            ext = ext.lower()
                            if ext not in report["file_stats"]["types"]:
                                report["file_stats"]["types"][ext] = 0
                            report["file_stats"]["types"][ext] += 1
            except:
                logger.warning("无法完成文件统计")
            
            return report
        except Exception as e:
            logger.error(f"生成仓库报告时出错: {e}")
            return {"error": str(e)}
    
    def format_repository_report(self, report):
        """
        格式化仓库报告为可读文本
        
        Args:
            report (dict): 仓库报告数据
            
        Returns:
            str: 格式化的报告文本
        """
        if "error" in report:
            return f"生成报告时出错: {report['error']}"
        
        # 基本信息
        sections = [
            f"{Fore.BLUE}{Style.BRIGHT}仓库: {report['name']}{Style.RESET_ALL}",
            f"{Fore.CYAN}路径: {Style.RESET_ALL}{report['path']}",
            f"{Fore.CYAN}当前分支: {Style.RESET_ALL}{report['current_branch']}",
            f"{Fore.CYAN}分支数量: {Style.RESET_ALL}{len(report['branches'])}",
            f"{Fore.CYAN}远程仓库: {Style.RESET_ALL}{len(report['remotes'])}"
        ]
        
        # 远程仓库
        if report["remotes"]:
            remote_items = [f"\n{Fore.YELLOW}远程仓库:{Style.RESET_ALL}"]
            for name, url in report["remotes"].items():
                remote_items.append(f"  {name}: {url}")
            sections.append("\n".join(remote_items))
        
        # 提交统计
        sections.append(f"\n{Fore.YELLOW}提交统计:{Style.RESET_ALL}")
        sections.append(f"  总提交数: {report['commit_counts'].get('total', 0)}")
        sections.append(f"  最近提交数: {report['commit_counts'].get('recent', 0)}")
        
        # 贡献者统计
        if report["contributors"]:
            sections.append(f"\n{Fore.YELLOW}贡献者统计:{Style.RESET_ALL}")
            
            table_data = []
            for author, stats in report["contributors"].items():
                table_data.append([
                    author,
                    stats["commits"],
                    stats["insertions"],
                    stats["deletions"]
                ])
            
            table = tabulate(
                table_data,
                headers=["贡献者", "提交数", "添加行数", "删除行数"],
                tablefmt="simple"
            )
            sections.append(table)
        
        # 最近提交
        if report["recent_commits"]:
            sections.append(f"\n{Fore.YELLOW}最近提交:{Style.RESET_ALL}")
            
            table_data = []
            for commit in report["recent_commits"]:
                date_str = commit["date"].strftime(self.date_format)
                message = commit["message"]
                if len(message) > 50:
                    message = message[:47] + "..."
                
                table_data.append([
                    commit["short_hash"],
                    date_str,
                    commit["author"],
                    message
                ])
            
            table = tabulate(
                table_data,
                headers=["提交", "日期", "作者", "消息"],
                tablefmt="simple"
            )
            sections.append(table)
        
        # 文件统计
        if report["file_stats"]["total"] > 0:
            sections.append(f"\n{Fore.YELLOW}文件统计:{Style.RESET_ALL}")
            sections.append(f"  总文件数: {report['file_stats']['total']}")
            
            if report["file_stats"]["types"]:
                sections.append("  文件类型:")
                
                table_data = []
                for ext, count in sorted(report["file_stats"]["types"].items(), key=lambda x: x[1], reverse=True)[:10]:
                    percentage = (count / report["file_stats"]["total"]) * 100
                    table_data.append([
                        ext if ext else "(无扩展名)",
                        count,
                        f"{percentage:.1f}%"
                    ])
                
                table = tabulate(
                    table_data,
                    headers=["类型", "数量", "百分比"],
                    tablefmt="simple"
                )
                sections.append("  " + table.replace("\n", "\n  "))
        
        return "\n".join(sections) 