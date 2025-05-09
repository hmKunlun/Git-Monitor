#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Git命令解析器
"""

import os
import sys
import unittest

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gitmonitor.parser import GitCommandParser

class TestGitCommandParser(unittest.TestCase):
    """测试Git命令解析器类"""
    
    def setUp(self):
        """设置测试环境"""
        self.parser = GitCommandParser()
    
    def test_parse_init(self):
        """测试解析git init命令"""
        cmd = "git init"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "init")
        self.assertEqual(result["command"], cmd)
        
        # 测试带参数的init
        cmd = "git init --bare my_repo"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "init")
        self.assertTrue(result["parsed_args"]["is_bare"])
        self.assertEqual(result["parsed_args"]["directory"], "--bare my_repo")
    
    def test_parse_clone(self):
        """测试解析git clone命令"""
        cmd = "git clone https://github.com/user/repo.git"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "clone")
        self.assertEqual(result["parsed_args"]["repository_url"], "https://github.com/user/repo.git")
        self.assertEqual(result["parsed_args"]["destination"], "repo")
        
        # 测试带参数的clone
        cmd = "git clone https://github.com/user/repo.git my_local_repo --depth 1 --branch main"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "clone")
        self.assertEqual(result["parsed_args"]["repository_url"], "https://github.com/user/repo.git")
        self.assertEqual(result["parsed_args"]["destination"], "my_local_repo")
        self.assertEqual(result["parsed_args"]["depth"], "1")
        self.assertEqual(result["parsed_args"]["branch"], "main")
    
    def test_parse_branch(self):
        """测试解析git branch命令"""
        # 测试列出分支
        cmd = "git branch"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "branch")
        self.assertTrue(result["parsed_args"]["is_list"])
        
        # 测试创建分支
        cmd = "git branch new-feature"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "branch")
        self.assertFalse(result["parsed_args"]["is_list"])
        self.assertEqual(result["parsed_args"]["branch_name"], "new-feature")
        
        # 测试删除分支
        cmd = "git branch -d old-feature"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "branch")
        self.assertTrue(result["parsed_args"]["is_delete"])
        self.assertEqual(result["parsed_args"]["branch_name"], "old-feature")
    
    def test_parse_checkout(self):
        """测试解析git checkout命令"""
        # 测试切换分支
        cmd = "git checkout main"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "checkout")
        self.assertEqual(result["parsed_args"]["branch_name"], "main")
        self.assertFalse(result["parsed_args"]["create_new"])
        
        # 测试创建并切换到新分支
        cmd = "git checkout -b feature/new-stuff"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "checkout")
        self.assertEqual(result["parsed_args"]["branch_name"], "feature/new-stuff")
        self.assertTrue(result["parsed_args"]["create_new"])
    
    def test_parse_add(self):
        """测试解析git add命令"""
        # 测试添加单个文件
        cmd = "git add file.txt"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "add")
        self.assertEqual(result["parsed_args"]["files"], ["file.txt"])
        self.assertFalse(result["parsed_args"]["all"])
        
        # 测试添加所有文件
        cmd = "git add ."
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "add")
        self.assertTrue(result["parsed_args"]["all"])
        
        # 测试添加多个文件
        cmd = "git add file1.txt file2.txt file3.txt"
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "add")
        self.assertEqual(result["parsed_args"]["files"], ["file1.txt", "file2.txt", "file3.txt"])
        self.assertFalse(result["parsed_args"]["all"])
    
    def test_parse_commit(self):
        """测试解析git commit命令"""
        # 测试基本提交
        cmd = "git commit -m \"Add new feature\""
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "commit")
        self.assertEqual(result["parsed_args"]["message"], "\"Add")
        
        # 测试带参数的提交
        cmd = "git commit -am \"Fix bug\""
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "commit")
        self.assertTrue(result["parsed_args"]["all"])
        
        # 测试修改上一次提交
        cmd = "git commit --amend -m \"Update commit message\""
        result = self.parser.parse_command(cmd)
        
        self.assertEqual(result["type"], "commit")
        self.assertTrue(result["parsed_args"]["amend"])
    
    def test_non_git_command(self):
        """测试非Git命令"""
        cmd = "ls -la"
        result = self.parser.parse_command(cmd)
        
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 