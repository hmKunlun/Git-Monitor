#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控工具 - GitHub仓库创建脚本 (Python版)
用于初始化Git仓库并上传项目文件到GitHub
跨平台支持：Windows、Linux和macOS
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

# 控制台颜色（兼容不同平台）
class Colors:
    """控制台颜色类（支持Windows和ANSI终端）"""
    def __init__(self):
        # Windows控制台颜色支持检测
        self.use_colors = True
        if sys.platform == 'win32':
            try:
                # 尝试为Windows启用ANSI颜色支持
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                # 如果失败，禁用颜色
                self.use_colors = False
    
    def red(self, text):
        """红色文本"""
        if not self.use_colors:
            return text
        return f"\033[0;31m{text}\033[0m"
        
    def green(self, text):
        """绿色文本"""
        if not self.use_colors:
            return text
        return f"\033[0;32m{text}\033[0m"
        
    def yellow(self, text):
        """黄色文本"""
        if not self.use_colors:
            return text
        return f"\033[0;33m{text}\033[0m"
        
    def blue(self, text):
        """蓝色文本"""
        if not self.use_colors:
            return text
        return f"\033[0;34m{text}\033[0m"

# 初始化颜色
colors = Colors()

def print_header():
    """打印脚本标题"""
    print(colors.blue("=" * 60))
    print(colors.blue("          Git命令监控工具 - GitHub仓库创建脚本          "))
    print(colors.blue("=" * 60))
    print()

def run_command(command, check=True, shell=True):
    """执行命令并返回结果状态"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=check, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        return True, result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.returncode, '', str(e)
    except Exception as e:
        return False, -1, '', str(e)

def check_git_installed():
    """检查Git是否已安装"""
    print(f"{colors.yellow('[信息]')} 检查Git是否已安装...")
    success, _, _, _ = run_command("git --version", check=False)
    
    if not success:
        print(f"{colors.red('[错误]')} 未检测到Git。请先安装Git。")
        if sys.platform == 'win32':
            print("下载地址: https://git-scm.com/download/win")
        elif sys.platform == 'darwin':
            print("安装命令: brew install git")
        else:
            print("Ubuntu/Debian: sudo apt install git")
            print("Fedora/RHEL: sudo dnf install git")
        return False
    return True

def get_repo_info():
    """获取GitHub仓库信息"""
    # 尝试使用直接的URL输入
    repo_url = input("请输入GitHub仓库URL或按Enter继续设置: ").strip()
    if repo_url:
        if not repo_url.endswith('.git'):
            repo_url = repo_url + '.git'
        return repo_url
    
    # 如果用户选择手动配置
    print("\n" + colors.yellow("[信息]") + " 请提供GitHub账户和仓库信息:")
    github_user = input("GitHub用户名: ").strip()
    if not github_user:
        print(f"{colors.red('[错误]')} 用户名不能为空。")
        return None
    
    repo_name = input("仓库名 (例如: git-command-monitor): ").strip()
    if not repo_name:
        print(f"{colors.red('[错误]')} 仓库名不能为空。")
        return None
    
    repo_url = f"https://github.com/{github_user}/{repo_name}.git"
    print(f"{colors.yellow('[信息]')} 将使用仓库URL: {repo_url}")
    
    confirm = input("是否正确？(y/n): ").strip().lower()
    if confirm != 'y':
        print(f"{colors.yellow('[信息]')} 请重新运行脚本并提供正确的信息。")
        return None
    
    # 询问是否需要在GitHub上创建仓库
    create_repo = input("\n是否需要先在GitHub上创建仓库？(y/n): ").strip().lower()
    if create_repo == 'y':
        print(f"{colors.yellow('[信息]')} 请按照以下步骤在GitHub上创建仓库：")
        print("1. 访问 https://github.com/new")
        print(f"2. 仓库名设置为: {repo_name}")
        print("3. 选择公开或私有")
        print("4. 不要初始化README、.gitignore或许可证")
        print("5. 点击'创建仓库'")
        input("\n完成后按Enter继续...")
    
    return repo_url

def create_directory_structure():
    """创建必要的目录结构"""
    print(f"{colors.yellow('[信息]')} 创建必要的目录结构...")
    
    # 创建目录
    for dir_name in ['data', 'logs', 'reports']:
        os.makedirs(dir_name, exist_ok=True)
        Path(os.path.join(dir_name, '.gitkeep')).touch()
    
    # 复制配置文件
    if not os.path.exists('config.json') and os.path.exists('config.example.json'):
        print(f"{colors.yellow('[信息]')} 复制配置文件模板...")
        shutil.copy2('config.example.json', 'config.json')
        print(f"{colors.green('[成功]')} 已创建配置文件。")
    elif not os.path.exists('config.json'):
        print(f"{colors.yellow('[警告]')} 未找到config.example.json，请确保创建一个config.json配置文件。")
    
    print(f"{colors.green('[成功]')} 目录结构创建完成。")

def setup_git_repo(repo_url):
    """设置Git仓库并推送到GitHub"""
    # 初始化Git仓库
    print(f"\n{colors.yellow('[信息]')} 正在初始化Git仓库...")
    success, code, _, stderr = run_command("git init")
    if not success:
        print(f"{colors.red('[错误]')} 初始化Git仓库失败: {stderr}")
        return False
    print(f"{colors.green('[成功]')} Git仓库初始化完成。")
    
    # 添加所有文件
    print(f"\n{colors.yellow('[信息]')} 添加文件到Git仓库...")
    success, code, _, stderr = run_command("git add .")
    if not success:
        print(f"{colors.red('[错误]')} 添加文件失败: {stderr}")
        return False
    print(f"{colors.green('[成功]')} 文件已添加到仓库。")
    
    # 提交所有文件
    print(f"\n{colors.yellow('[信息]')} 提交文件...")
    success, code, _, stderr = run_command('git commit -m "Initial commit: Git Command Monitor Tool"')
    if not success:
        print(f"{colors.red('[错误]')} 提交文件失败: {stderr}")
        print("提示: 使用以下命令配置Git用户")
        print('  git config --global user.name "你的名字"')
        print('  git config --global user.email "你的邮箱"')
        return False
    print(f"{colors.green('[成功]')} 文件已提交。")
    
    # 添加远程仓库
    print(f"\n{colors.yellow('[信息]')} 添加远程仓库...")
    success, code, _, stderr = run_command(f'git remote add origin "{repo_url}"')
    if not success:
        print(f"{colors.red('[错误]')} 添加远程仓库失败: {stderr}")
        return False
    print(f"{colors.green('[成功]')} 远程仓库已添加。")
    
    # 询问分支名称
    default_branch = input("\n请输入要使用的默认分支名称 (通常是main或master，默认为main): ").strip()
    if not default_branch:
        default_branch = "main"
        print(f"{colors.yellow('[信息]')} 使用默认分支名: {default_branch}")
    
    # 重命名分支
    success, code, _, stderr = run_command(f'git branch -M {default_branch}')
    if not success:
        print(f"{colors.red('[错误]')} 重命名分支失败: {stderr}")
        return False
    
    # 询问是否推送
    push_now = input("\n是否立即推送到远程仓库？(y/n): ").strip().lower()
    if push_now == 'y':
        print(f"\n{colors.yellow('[信息]')} 推送到远程仓库...")
        success, code, _, stderr = run_command(f'git push -u origin {default_branch}')
        if not success:
            print(f"{colors.red('[错误]')} 推送失败: {stderr}")
            print("你可能需要通过浏览器授权GitHub访问。")
            return False
        print(f"{colors.green('[成功]')} 代码已成功推送到远程仓库。")
    else:
        print(f"\n{colors.yellow('[信息]')} 跳过推送。你可以稍后使用以下命令手动推送:")
        print(f"  git push -u origin {default_branch}")
    
    return True

def main():
    """主函数"""
    print_header()
    
    # 检查Git是否已安装
    if not check_git_installed():
        return 1
    
    # 获取仓库信息
    repo_url = get_repo_info()
    if not repo_url:
        return 1
    
    # 创建目录结构
    create_directory_structure()
    
    # 设置Git仓库
    if not setup_git_repo(repo_url):
        return 1
    
    # 完成
    print()
    print(colors.blue("=" * 60))
    print(colors.green("                      操作完成！                      "))
    print(colors.blue("=" * 60))
    print()
    print("下一步：")
    print("1. 在GitHub上查看你的仓库")
    print("2. 添加详细的README.md描述")
    print("3. 邀请贡献者并分享你的项目")
    print()
    print(colors.green("祝你的开源项目成功！"))
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n操作已取消。")
        sys.exit(1) 