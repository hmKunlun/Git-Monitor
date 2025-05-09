"""
数据存储模块，负责保存和检索Git操作记录
"""
import os
import sqlite3
import json
import logging
from datetime import datetime
from gitmonitor.utils import ensure_dir_exists

logger = logging.getLogger(__name__)

class GitHistoryStorage:
    """Git操作历史存储类"""
    
    def __init__(self, config=None):
        """初始化存储类"""
        if config is None:
            config = {}
        
        self.storage_path = config.get("storage_path", "./data")
        self.db_file = config.get("database_file", "git_history.db")
        
        ensure_dir_exists(self.storage_path)
        self.db_path = os.path.join(self.storage_path, self.db_file)
        
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建Git命令记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS git_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    repository TEXT,
                    working_dir TEXT,
                    description TEXT,
                    result TEXT,
                    exit_code INTEGER
                )
            ''')
            
            # 创建提交记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id INTEGER,
                    commit_hash TEXT,
                    author TEXT,
                    commit_date DATETIME,
                    message TEXT,
                    files_changed INTEGER,
                    insertions INTEGER,
                    deletions INTEGER,
                    FOREIGN KEY (command_id) REFERENCES git_commands(id) ON DELETE CASCADE
                )
            ''')
            
            # 创建文件变更表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_id INTEGER,
                    filename TEXT,
                    change_type TEXT,
                    insertions INTEGER,
                    deletions INTEGER,
                    content BLOB,
                    FOREIGN KEY (commit_id) REFERENCES commits(id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"初始化数据库时出错: {e}")
            raise
    
    def store_git_command(self, command, repository=None, working_dir=None, description=None, result=None, exit_code=None):
        """存储Git命令记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''INSERT INTO git_commands (command, repository, working_dir, description, result, exit_code) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (command, repository, working_dir, description, result, exit_code)
            )
            
            command_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"已存储Git命令: {command}")
            return command_id
        except Exception as e:
            logger.error(f"存储Git命令时出错: {e}")
            raise
    
    def store_commit(self, command_id, commit_hash, author, commit_date, message, files_changed, insertions, deletions):
        """存储提交记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''INSERT INTO commits (command_id, commit_hash, author, commit_date, message, files_changed, insertions, deletions) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (command_id, commit_hash, author, commit_date, message, files_changed, insertions, deletions)
            )
            
            commit_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"已存储提交记录: {commit_hash}")
            return commit_id
        except Exception as e:
            logger.error(f"存储提交记录时出错: {e}")
            raise
    
    def store_file_change(self, commit_id, filename, change_type, insertions, deletions, content=None):
        """存储文件变更记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''INSERT INTO file_changes (commit_id, filename, change_type, insertions, deletions, content) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (commit_id, filename, change_type, insertions, deletions, content)
            )
            
            file_change_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"已存储文件变更: {filename}")
            return file_change_id
        except Exception as e:
            logger.error(f"存储文件变更时出错: {e}")
            raise
    
    def get_recent_commands(self, limit=10, repository=None):
        """获取最近的Git命令记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT id, command, timestamp, repository, description, result FROM git_commands"
            params = []
            
            if repository:
                query += " WHERE repository = ?"
                params.append(repository)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            commands = []
            for row in results:
                commands.append({
                    "id": row[0],
                    "command": row[1],
                    "timestamp": row[2],
                    "repository": row[3],
                    "description": row[4],
                    "result": row[5]
                })
            
            return commands
        except Exception as e:
            logger.error(f"获取Git命令记录时出错: {e}")
            return []
    
    def get_commit_details(self, commit_id):
        """获取提交详情"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取提交基本信息
            cursor.execute(
                "SELECT commit_hash, author, commit_date, message, files_changed, insertions, deletions FROM commits WHERE id = ?",
                (commit_id,)
            )
            commit_row = cursor.fetchone()
            
            if not commit_row:
                conn.close()
                return None
            
            commit = {
                "commit_hash": commit_row[0],
                "author": commit_row[1],
                "commit_date": commit_row[2],
                "message": commit_row[3],
                "files_changed": commit_row[4],
                "insertions": commit_row[5],
                "deletions": commit_row[6],
                "file_changes": []
            }
            
            # 获取文件变更信息
            cursor.execute(
                "SELECT filename, change_type, insertions, deletions FROM file_changes WHERE commit_id = ?",
                (commit_id,)
            )
            file_rows = cursor.fetchall()
            
            for file_row in file_rows:
                commit["file_changes"].append({
                    "filename": file_row[0],
                    "change_type": file_row[1],
                    "insertions": file_row[2],
                    "deletions": file_row[3]
                })
            
            conn.close()
            return commit
        except Exception as e:
            logger.error(f"获取提交详情时出错: {e}")
            return None
    
    def search_commands(self, query, limit=50):
        """搜索Git命令记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            search_term = f"%{query}%"
            cursor.execute(
                """SELECT id, command, timestamp, repository, description 
                   FROM git_commands 
                   WHERE command LIKE ? OR repository LIKE ? OR description LIKE ? 
                   ORDER BY timestamp DESC LIMIT ?""",
                (search_term, search_term, search_term, limit)
            )
            results = cursor.fetchall()
            conn.close()
            
            commands = []
            for row in results:
                commands.append({
                    "id": row[0],
                    "command": row[1],
                    "timestamp": row[2],
                    "repository": row[3],
                    "description": row[4]
                })
            
            return commands
        except Exception as e:
            logger.error(f"搜索Git命令时出错: {e}")
            return []
    
    def get_repository_stats(self, repository):
        """获取仓库统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # 命令统计
            cursor.execute(
                """SELECT COUNT(*) FROM git_commands WHERE repository = ?""",
                (repository,)
            )
            stats["total_commands"] = cursor.fetchone()[0]
            
            # 命令类型统计
            cursor.execute(
                """SELECT command, COUNT(*) as count 
                   FROM git_commands 
                   WHERE repository = ? 
                   GROUP BY substr(command, 1, instr(command || ' ', ' '))
                   ORDER BY count DESC""",
                (repository,)
            )
            stats["command_types"] = {row[0].split()[0]: row[1] for row in cursor.fetchall()}
            
            # 提交统计
            cursor.execute(
                """SELECT COUNT(*), SUM(c.files_changed), SUM(c.insertions), SUM(c.deletions)
                   FROM commits c
                   JOIN git_commands g ON c.command_id = g.id
                   WHERE g.repository = ?""",
                (repository,)
            )
            commit_stats = cursor.fetchone()
            if commit_stats and commit_stats[0]:
                stats["total_commits"] = commit_stats[0]
                stats["total_files_changed"] = commit_stats[1] or 0
                stats["total_insertions"] = commit_stats[2] or 0
                stats["total_deletions"] = commit_stats[3] or 0
            else:
                stats["total_commits"] = 0
                stats["total_files_changed"] = 0
                stats["total_insertions"] = 0
                stats["total_deletions"] = 0
            
            conn.close()
            return stats
        except Exception as e:
            logger.error(f"获取仓库统计信息时出错: {e}")
            return {} 