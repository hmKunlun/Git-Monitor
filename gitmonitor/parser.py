"""
Git命令解析模块，用于解析Git命令并提取相关信息
"""
import re
import os
import logging
import git
import subprocess
from datetime import datetime
from gitmonitor.utils import get_git_command_description

logger = logging.getLogger(__name__)

class GitCommandParser:
    """Git命令解析器类"""
    
    def __init__(self):
        """初始化Git命令解析器"""
        self.git_cmd_patterns = {
            "init": r"git\s+init\s*(.*)",
            "clone": r"git\s+clone\s+(.*)",
            "branch": r"git\s+branch\s+(.*)",
            "checkout": r"git\s+checkout\s+(.*)",
            "add": r"git\s+add\s+(.*)",
            "commit": r"git\s+commit\s+(.*)",
            "merge": r"git\s+merge\s+(.*)",
            "push": r"git\s+push\s+(.*)",
            "pull": r"git\s+pull\s+(.*)",
            "cherry-pick": r"git\s+cherry-pick\s+(.*)"
        }
    
    def parse_command(self, command):
        """
        解析Git命令
        
        Args:
            command (str): Git命令字符串
            
        Returns:
            dict: 解析结果，包含命令类型和详细参数
        """
        if not command.startswith("git "):
            return None
        
        result = {
            "command": command.strip(),
            "type": None,
            "args": None,
            "description": get_git_command_description(command),
            "repository": None,
            "parsed_args": {}
        }
        
        for cmd_type, pattern in self.git_cmd_patterns.items():
            match = re.match(pattern, command)
            if match:
                result["type"] = cmd_type
                result["args"] = match.group(1).strip() if match.groups() else ""
                
                # 根据命令类型进一步解析参数
                parse_method = getattr(self, f"_parse_{cmd_type}", None)
                if parse_method:
                    result["parsed_args"] = parse_method(result["args"])
                
                break
        
        return result
    
    def _parse_init(self, args):
        """解析git init命令参数"""
        return {
            "directory": args if args else os.getcwd(),
            "is_bare": "--bare" in args
        }
    
    def _parse_clone(self, args):
        """解析git clone命令参数"""
        parts = args.split()
        repo_url = parts[0] if parts else ""
        destination = parts[1] if len(parts) > 1 else os.path.basename(repo_url.rstrip("/"))
        if destination.endswith(".git"):
            destination = destination[:-4]
            
        return {
            "repository_url": repo_url,
            "destination": destination,
            "depth": self._extract_option(args, "--depth"),
            "branch": self._extract_option(args, "--branch") or self._extract_option(args, "-b")
        }
    
    def _parse_branch(self, args):
        """解析git branch命令参数"""
        parts = args.split()
        
        result = {
            "is_list": not parts or parts[0].startswith("-"),
            "is_delete": "-d" in parts or "-D" in parts,
            "branch_name": None
        }
        
        # 确定分支名称
        for i, part in enumerate(parts):
            if not part.startswith("-") and (i == 0 or not parts[i-1] in ["-b", "-m", "-M"]):
                result["branch_name"] = part
                break
        
        return result
    
    def _parse_checkout(self, args):
        """解析git checkout命令参数"""
        parts = args.split()
        
        result = {
            "branch_name": None,
            "create_new": "-b" in parts,
            "is_file": False
        }
        
        # 处理分支名或文件名
        for i, part in enumerate(parts):
            if not part.startswith("-"):
                # 如果前一个部分是-b，这是新分支的名称
                if i > 0 and parts[i-1] == "-b":
                    result["branch_name"] = part
                    break
                # 否则它可能是分支名或文件路径
                else:
                    result["branch_name"] = part
                    # 尝试确定是分支还是文件
                    try:
                        if os.path.exists(part) and not os.path.exists(os.path.join(".git", "refs", "heads", part)):
                            result["is_file"] = True
                    except:
                        pass
                    break
        
        return result
    
    def _parse_add(self, args):
        """解析git add命令参数"""
        return {
            "files": args.split() if args else ["."],
            "all": args.strip() == "." or args.strip() == "-A" or args.strip() == "--all"
        }
    
    def _parse_commit(self, args):
        """解析git commit命令参数"""
        commit_msg = self._extract_option(args, "-m", is_valued=True)
        if not commit_msg and "--message=" in args:
            match = re.search(r'--message="([^"]*)"', args) or re.search(r"--message='([^']*)'", args)
            if match:
                commit_msg = match.group(1)
        
        return {
            "message": commit_msg,
            "amend": "--amend" in args,
            "all": "-a" in args or "--all" in args
        }
    
    def _parse_merge(self, args):
        """解析git merge命令参数"""
        parts = args.split()
        branch_name = parts[0] if parts and not parts[0].startswith("-") else None
        
        return {
            "branch_name": branch_name,
            "no_ff": "--no-ff" in args,
            "ff_only": "--ff-only" in args,
            "squash": "--squash" in args
        }
    
    def _parse_push(self, args):
        """解析git push命令参数"""
        parts = args.split()
        remote = None
        branch = None
        
        for i, part in enumerate(parts):
            if not part.startswith("-"):
                if remote is None:
                    remote = part
                elif branch is None:
                    branch = part
                break
        
        return {
            "remote": remote or "origin",
            "branch": branch,
            "force": "-f" in args or "--force" in args,
            "all": "--all" in args
        }
    
    def _parse_pull(self, args):
        """解析git pull命令参数"""
        parts = args.split()
        remote = None
        branch = None
        
        for i, part in enumerate(parts):
            if not part.startswith("-"):
                if remote is None:
                    remote = part
                elif branch is None:
                    branch = part
                break
        
        return {
            "remote": remote or "origin",
            "branch": branch,
            "rebase": "--rebase" in args
        }
    
    def _parse_cherry_pick(self, args):
        """解析git cherry-pick命令参数"""
        parts = args.split()
        commit_hash = parts[0] if parts and not parts[0].startswith("-") else None
        
        return {
            "commit_hash": commit_hash,
            "no_commit": "-n" in args or "--no-commit" in args,
            "edit": "-e" in args or "--edit" in args,
            "continue": "--continue" in args
        }
    
    def _extract_option(self, args, option, is_valued=False):
        """
        从参数字符串中提取选项值
        
        Args:
            args (str): 参数字符串
            option (str): 要提取的选项，如 "--depth"
            is_valued (bool): 该选项是否有值
            
        Returns:
            str or bool: 如果选项存在，返回其值或True；否则返回None或False
        """
        if not is_valued:
            return option in args.split()
        
        # 处理形如 "--option=value" 的参数
        pattern = f"{option}[= ]([^\\s]+)"
        match = re.search(pattern, args)
        if match:
            return match.group(1)
        
        # 处理形如 "--option value" 的参数
        parts = args.split()
        for i, part in enumerate(parts):
            if part == option and i + 1 < len(parts):
                return parts[i + 1]
        
        return None
    
    def get_repository_from_command(self, command, working_dir):
        """
        从命令和工作目录中获取仓库信息
        
        Args:
            command (str): Git命令字符串
            working_dir (str): 工作目录路径
            
        Returns:
            str: 仓库名称
        """
        try:
            parsed = self.parse_command(command)
            if not parsed:
                return None
            
            # 对于克隆命令，尝试从URL中提取仓库名
            if parsed["type"] == "clone" and "repository_url" in parsed["parsed_args"]:
                repo_url = parsed["parsed_args"]["repository_url"]
                repo_name = os.path.basename(repo_url.rstrip("/"))
                if repo_name.endswith(".git"):
                    repo_name = repo_name[:-4]
                return repo_name
            
            # 对于其他命令，尝试从工作目录中获取仓库名
            if working_dir:
                try:
                    repo = git.Repo(working_dir, search_parent_directories=True)
                    remote_url = None
                    try:
                        remote_url = repo.remotes.origin.url
                    except:
                        pass
                    
                    if remote_url:
                        repo_name = os.path.basename(remote_url.rstrip("/"))
                        if repo_name.endswith(".git"):
                            repo_name = repo_name[:-4]
                        return repo_name
                    
                    # 如果没有远程URL，使用目录名
                    return os.path.basename(repo.working_dir)
                except git.exc.InvalidGitRepositoryError:
                    # 如果初始化命令，使用目录名作为仓库名
                    if parsed["type"] == "init":
                        init_dir = parsed["parsed_args"].get("directory", working_dir)
                        return os.path.basename(os.path.abspath(init_dir))
            
            return None
        except Exception as e:
            logger.error(f"获取仓库信息时出错: {e}")
            return None
    
    def extract_commit_info(self, repo_path, commit_hash):
        """
        提取提交信息
        
        Args:
            repo_path (str): 仓库路径
            commit_hash (str): 提交哈希值
            
        Returns:
            dict: 提交信息
        """
        try:
            repo = git.Repo(repo_path)
            commit = repo.commit(commit_hash)
            
            stats = commit.stats
            return {
                "commit_hash": commit.hexsha,
                "author": f"{commit.author.name} <{commit.author.email}>",
                "commit_date": datetime.fromtimestamp(commit.committed_date),
                "message": commit.message,
                "files_changed": len(stats.files),
                "insertions": stats.total["insertions"],
                "deletions": stats.total["deletions"],
                "files": stats.files
            }
        except Exception as e:
            logger.error(f"提取提交信息时出错: {e}")
            return None
    
    def parse_diff(self, repo_path, commit_hash):
        """
        解析提交差异
        
        Args:
            repo_path (str): 仓库路径
            commit_hash (str): 提交哈希值
            
        Returns:
            list: 文件变更列表
        """
        try:
            repo = git.Repo(repo_path)
            commit = repo.commit(commit_hash)
            
            changes = []
            # 获取父提交（如果存在）
            parent = commit.parents[0] if commit.parents else None
            
            # 对于每个更改的文件
            for file_path, stats in commit.stats.files.items():
                change_type = "modified"
                
                # 尝试确定变更类型
                if parent:
                    try:
                        # 文件在当前提交中存在，但在父提交中不存在
                        parent.tree[file_path]
                    except:
                        change_type = "added"
                    
                    try:
                        # 文件在当前提交中不存在，但在父提交中存在
                        commit.tree[file_path]
                    except:
                        change_type = "deleted"
                
                # 提取文件内容（如果不是删除）
                content = None
                if change_type != "deleted":
                    try:
                        content = commit.tree[file_path].data_stream.read().decode('utf-8', errors='ignore')
                    except:
                        pass
                
                changes.append({
                    "filename": file_path,
                    "change_type": change_type,
                    "insertions": stats["insertions"],
                    "deletions": stats["deletions"],
                    "content": content
                })
            
            return changes
        except Exception as e:
            logger.error(f"解析提交差异时出错: {e}")
            return [] 