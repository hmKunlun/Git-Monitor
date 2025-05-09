#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控 - 开机自启动配置工具
支持将应用添加到Windows启动项，实现开机自启动
"""

import os
import sys
import winreg
import platform
import subprocess
from pathlib import Path

def create_shortcut(target_path, shortcut_path, working_dir=None, description=None):
    """
    创建Windows快捷方式
    
    Args:
        target_path (str): 目标文件路径
        shortcut_path (str): 快捷方式路径
        working_dir (str, optional): 工作目录
        description (str, optional): 描述
    
    Returns:
        bool: 是否成功创建
    """
    try:
        # 确保.lnk扩展名
        if not shortcut_path.endswith('.lnk'):
            shortcut_path += '.lnk'
        
        # 使用PowerShell创建快捷方式，因为它更可靠
        # 创建Shell对象
        shortcut_dir = os.path.dirname(shortcut_path)
        if not os.path.exists(shortcut_dir):
            os.makedirs(shortcut_dir)
        
        # 构建PowerShell命令
        ps_command = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{target_path}"
        """
        
        if working_dir:
            ps_command += f'$Shortcut.WorkingDirectory = "{working_dir}"\n'
        
        if description:
            ps_command += f'$Shortcut.Description = "{description}"\n'
        
        ps_command += '$Shortcut.Save()\n'
        
        # 执行PowerShell命令
        subprocess.run(["powershell", "-Command", ps_command], 
                       capture_output=True, 
                       check=True)
        
        return os.path.exists(shortcut_path)
    except Exception as e:
        print(f"创建快捷方式失败: {e}")
        return False

def add_to_registry():
    """
    将应用添加到注册表启动项
    
    Returns:
        bool: 是否成功添加
    """
    try:
        # 获取当前可执行文件路径
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的路径
            exe_path = sys.executable
        else:
            # 开发环境使用脚本路径
            script_path = os.path.abspath(__file__)
            # 使用上级目录的tray_app.py
            exe_path = os.path.normpath(os.path.join(os.path.dirname(script_path), "tray_app.py"))
        
        # 设置应用名称
        app_name = "GitCommandMonitor"
        
        # 打开注册表键
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        # 使用pythonw.exe运行脚本（无控制台窗口）
        # 如果是打包后的exe，直接使用exe路径
        if exe_path.endswith('.py'):
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            command = f'"{python_exe}" "{exe_path}"'
        else:
            command = f'"{exe_path}"'
        
        # 设置注册表值
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"添加到注册表失败: {e}")
        return False

def remove_from_registry():
    """
    从注册表启动项中移除应用
    
    Returns:
        bool: 是否成功移除
    """
    try:
        # 设置应用名称
        app_name = "GitCommandMonitor"
        
        # 打开注册表键
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        # 尝试删除注册表值
        try:
            winreg.DeleteValue(key, app_name)
        except FileNotFoundError:
            # 如果键不存在，则忽略
            pass
        
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"从注册表移除失败: {e}")
        return False

def add_to_startup_folder():
    """
    将应用添加到启动文件夹
    
    Returns:
        bool: 是否成功添加
    """
    try:
        # 获取当前可执行文件路径
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的路径
            exe_path = sys.executable
        else:
            # 开发环境使用脚本路径
            script_path = os.path.abspath(__file__)
            # 使用上级目录的tray_app.py
            exe_path = os.path.normpath(os.path.join(os.path.dirname(script_path), "tray_app.py"))
        
        # 获取启动文件夹路径
        startup_folder = os.path.join(
            os.environ["APPDATA"],
            r"Microsoft\Windows\Start Menu\Programs\Startup"
        )
        
        # 创建快捷方式
        shortcut_path = os.path.join(startup_folder, "GitCommandMonitor.lnk")
        
        # 设置工作目录
        working_dir = os.path.dirname(exe_path)
        
        # 创建快捷方式
        if exe_path.endswith('.py'):
            # 如果是Python脚本，使用pythonw.exe运行（无控制台窗口）
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            return create_shortcut(
                python_exe,
                shortcut_path,
                working_dir,
                "Git命令监控工具"
            )
        else:
            # 如果是exe，直接创建快捷方式
            return create_shortcut(
                exe_path,
                shortcut_path,
                working_dir,
                "Git命令监控工具"
            )
    except Exception as e:
        print(f"添加到启动文件夹失败: {e}")
        return False

def remove_from_startup_folder():
    """
    从启动文件夹中移除应用
    
    Returns:
        bool: 是否成功移除
    """
    try:
        # 获取启动文件夹路径
        startup_folder = os.path.join(
            os.environ["APPDATA"],
            r"Microsoft\Windows\Start Menu\Programs\Startup"
        )
        
        # 删除快捷方式
        shortcut_path = os.path.join(startup_folder, "GitCommandMonitor.lnk")
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
        
        return True
    except Exception as e:
        print(f"从启动文件夹移除失败: {e}")
        return False

def is_in_startup():
    """
    检查应用是否已设置为开机启动
    
    Returns:
        bool: 是否已设置开机启动
    """
    # 检查注册表
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        
        try:
            winreg.QueryValueEx(key, "GitCommandMonitor")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            # 不在注册表中，检查启动文件夹
            pass
    except Exception:
        # 如果无法访问注册表，则忽略
        pass
    
    # 检查启动文件夹
    startup_folder = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )
    shortcut_path = os.path.join(startup_folder, "GitCommandMonitor.lnk")
    
    return os.path.exists(shortcut_path)

def configure_startup():
    """
    配置开机启动（切换状态）
    
    如果当前已设置开机启动，则取消；
    如果当前未设置开机启动，则添加。
    
    Returns:
        bool: 新的开机启动状态（True表示已设置开机启动）
    """
    # 检查当前状态
    current_status = is_in_startup()
    
    if current_status:
        # 如果已设置开机启动，则移除
        remove_from_registry()
        remove_from_startup_folder()
        return False
    else:
        # 如果未设置开机启动，则添加
        # 优先使用注册表方法，如果失败则尝试启动文件夹方法
        if not add_to_registry():
            add_to_startup_folder()
        return True

if __name__ == "__main__":
    # 命令行工具模式
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ['add', 'enable', 'install']:
            if add_to_registry() or add_to_startup_folder():
                print("已成功设置开机启动！")
            else:
                print("设置开机启动失败！")
        elif sys.argv[1].lower() in ['remove', 'disable', 'uninstall']:
            remove_from_registry()
            remove_from_startup_folder()
            print("已取消开机启动！")
        elif sys.argv[1].lower() in ['status', 'check']:
            if is_in_startup():
                print("当前已设置开机启动")
            else:
                print("当前未设置开机启动")
        else:
            print("未知命令。用法：")
            print("  python startup_helper.py [add|remove|status]")
    else:
        # 切换状态
        if configure_startup():
            print("已成功设置开机启动！")
        else:
            print("已取消开机启动！") 