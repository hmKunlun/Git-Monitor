#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控工具 - 简化打包脚本
使用PyInstaller打包应用为可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_section(title):
    """打印分节标题"""
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print(f"{'-' * 60}")

def ensure_dir(directory):
    """确保目录存在"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def copy_file(src, dst):
    """复制文件"""
    try:
        shutil.copy2(src, dst)
        print(f"已复制: {os.path.basename(src)} -> {dst}")
    except Exception as e:
        print(f"复制文件失败 {src}: {e}")

def main():
    """主函数"""
    print_section("开始打包Git命令监控应用")
    
    # 获取当前工作目录
    work_dir = os.path.abspath(os.path.dirname(__file__))
    dist_dir = os.path.join(work_dir, "dist", "GitCommandMonitor")
    
    # 确保存在一个图标文件
    icon_path = os.path.join(work_dir, "app_icon.png")
    
    # 准备基本依赖
    print("安装PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                   check=False, capture_output=True)
    
    # 构建基本的PyInstaller命令
    print_section("开始构建应用")
    
    # 使用基本参数构建命令
    cmd = [
        "pyinstaller",
        "--name=GitCommandMonitor",
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--distpath={os.path.join(work_dir, 'dist')}",
        f"--workpath={os.path.join(work_dir, 'build')}",
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=matplotlib",
        "--hidden-import=pandas",
        "--hidden-import=jinja2",
        "--hidden-import=markdown",
        "--hidden-import=numpy",
        "--hidden-import=pkg_resources",
    ]
    
    # 添加图标设置（如果存在）
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
        cmd.extend(["--add-data", f"{icon_path};."])
    
    # 添加配置文件（如果存在）
    config_path = os.path.join(work_dir, "config.json")
    if os.path.exists(config_path):
        cmd.extend(["--add-data", f"{config_path};."])
    
    # 添加主程序脚本路径
    tray_script = os.path.join(work_dir, "tray_app.py")
    cmd.append(tray_script)
    
    # 执行PyInstaller命令
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    
    if result.returncode != 0:
        print_section("构建失败")
        print(f"PyInstaller 返回代码: {result.returncode}")
        print("尝试备用构建方法...")
        
        # 备用构建方法 - 最简单的命令行
        backup_cmd = [
            "pyinstaller",
            "--onedir",
            "--windowed",
            "--name=GitCommandMonitor",
            tray_script
        ]
        backup_result = subprocess.run(backup_cmd, check=False)
        
        if backup_result.returncode != 0:
            print("备用构建也失败了。请检查PyInstaller安装和依赖项。")
            return
    
    print_section("构建完成")
    
    # 创建必要目录
    for folder in ["data", "logs", "reports"]:
        folder_path = os.path.join(dist_dir, folder)
        ensure_dir(folder_path)
        print(f"创建目录: {folder}")
    
    # 复制其他脚本文件到dist目录
    for script in ["run_tray_hidden.py", "run_background.py", "background_monitor.py"]:
        script_path = os.path.join(work_dir, script)
        if os.path.exists(script_path):
            copy_file(script_path, dist_dir)
    
    # 创建README文件
    readme_path = os.path.join(dist_dir, "README.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("Git命令监控工具 - 使用说明\n")
        f.write("=====================================\n\n")
        f.write("1. 直接运行方式：\n")
        f.write("   - 双击 GitCommandMonitor.exe 启动系统托盘应用\n\n")
        f.write("2. 无窗口后台运行：\n")
        f.write("   - 双击 run_tray_hidden.py 以无窗口模式启动系统托盘应用\n\n")
        f.write("3. 纯后台监控（无界面）：\n")
        f.write("   - 双击 run_background.py 以无窗口模式启动后台监控服务\n\n")
        f.write("请确保Python环境已正确安装，并且安装了所需的依赖包。\n")
    
    print(f"打包完成！应用程序位于: {dist_dir}")
    print(f"系统托盘应用: {os.path.join(dist_dir, 'GitCommandMonitor.exe')}")
    print("也可使用 run_tray_hidden.py 在后台运行应用。")

if __name__ == "__main__":
    main() 