#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复PyInstaller的setuptools钩子问题
"""

import os
import sys
import platform

def fix_setuptools_hook():
    """
    修复PyInstaller的hook-setuptools.py文件中的版本检测问题
    """
    # 查找可能的PyInstaller安装路径
    python_path = os.path.dirname(sys.executable)
    possible_paths = [
        os.path.join(python_path, "Lib", "site-packages", "PyInstaller", "hooks", "hook-setuptools.py"),
        os.path.join(python_path, "lib", "site-packages", "PyInstaller", "hooks", "hook-setuptools.py"),
        os.path.join(python_path, "..", "Lib", "site-packages", "PyInstaller", "hooks", "hook-setuptools.py"),
        os.path.join(python_path, "lib", "python3.8", "site-packages", "PyInstaller", "hooks", "hook-setuptools.py"),
        # 添加额外的可能路径
        "C:\\Users\\86199\\AppData\\Local\\Programs\\Python\\Python38\\lib\\site-packages\\PyInstaller\\hooks\\hook-setuptools.py"
    ]
    
    hook_file = None
    for path in possible_paths:
        if os.path.exists(path):
            hook_file = path
            break
    
    if not hook_file:
        print("错误：无法找到PyInstaller的hook-setuptools.py文件")
        return False
    
    print(f"找到hook文件：{hook_file}")
    
    # 读取原始文件
    with open(hook_file, 'r') as f:
        content = f.read()
    
    # 创建备份
    with open(hook_file + '.bak', 'w') as f:
        f.write(content)
    
    # 修改版本检测逻辑
    fixed_content = content.replace(
        "if setuptools_info.version < (71, 0):",
        "if setuptools_info.version and setuptools_info.version < (71, 0):"
    )
    
    # 写入修复后的文件
    with open(hook_file, 'w') as f:
        f.write(fixed_content)
    
    print(f"成功修复hook文件：{hook_file}")
    return True

if __name__ == "__main__":
    if fix_setuptools_hook():
        print("修复完成！请重新尝试打包应用。")
    else:
        print("修复失败，请手动检查PyInstaller的setuptools钩子文件。") 