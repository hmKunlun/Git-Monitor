#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控 - 无窗口后台运行启动脚本
使用pythonw启动，无命令行窗口显示
"""

import os
import sys
import subprocess
import time
import datetime
from pathlib import Path

def get_script_path():
    """获取当前脚本的绝对路径"""
    return os.path.dirname(os.path.abspath(__file__))

def start_background_service():
    """启动后台服务"""
    # 获取脚本路径
    script_dir = get_script_path()
    
    # 获取Python路径和pythonw路径
    python_path = sys.executable
    pythonw_path = python_path.replace('python.exe', 'pythonw.exe')
    
    if not os.path.exists(pythonw_path):
        print("找不到pythonw.exe，无法在后台运行！")
        print(f"尝试路径: {pythonw_path}")
        print("请手动运行: python background_monitor.py")
        return False
    
    # 构建要运行的命令
    background_script = os.path.join(script_dir, "background_monitor.py")
    
    # 记录启动日志
    log_dir = os.path.join(script_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "startup.log")
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] 正在启动无窗口后台服务...\n")
    
    try:
        # 使用pythonw启动（无控制台窗口）
        process = subprocess.Popen(
            [pythonw_path, background_script],
            cwd=script_dir,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # 等待片刻检查进程是否正常启动
        time.sleep(2)
        
        if process.poll() is None:
            # 进程仍在运行，表示启动成功
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] 无窗口后台服务启动成功，进程ID: {process.pid}\n")
            
            print("Git命令监控已在后台启动！")
            print("服务将持续运行，即使关闭此窗口")
            print(f"启动日志已保存至: {log_file}")
            return True
        else:
            # 进程已退出，启动失败
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] 无窗口后台服务启动失败，退出代码: {process.returncode}\n")
            
            print("启动后台服务失败！")
            print(f"请查看日志获取详细信息: {log_file}")
            return False
            
    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] 启动错误: {e}\n")
        
        print(f"启动出错: {e}")
        return False

if __name__ == "__main__":
    start_background_service() 