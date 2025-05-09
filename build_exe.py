#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控 - 打包脚本
将应用打包为可执行文件，方便分发
"""

import os
import sys
import shutil
import subprocess
import time
import site
from pathlib import Path

def print_banner(title):
    """打印标题横幅"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def safe_remove_path(path):
    """安全地删除文件或目录，处理权限错误"""
    if not os.path.exists(path):
        return True
        
    for attempt in range(3):  # 尝试多次
        try:
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
            return True
        except PermissionError:
            print(f"无法删除 {path}，可能被其他进程占用。尝试结束相关进程...")
            
            # 如果是Windows，尝试结束进程
            if sys.platform == 'win32':
                try:
                    # 尝试结束进程
                    subprocess.run(["taskkill", "/F", "/IM", "GitCommandMonitor.exe"], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception as e:
                    print(f"结束进程时出错: {e}")
            
            print(f"等待5秒后重试 (尝试 {attempt+1}/3)...")
            time.sleep(5)
        except Exception as e:
            print(f"删除 {path} 时出错: {e}")
            return False
    
    print(f"警告：无法删除 {path}，将继续构建，可能会覆盖现有文件")
    return False

def create_custom_hooks():
    """创建自定义钩子来处理jaraco包依赖问题"""
    # 创建自定义的pkg_resources钩子
    with open("hook-pkg_resources.py", "w") as f:
        f.write("""
# hook-pkg_resources.py
from PyInstaller.utils.hooks import collect_all, copy_metadata

# 收集jaraco及其所有子模块
datas, binaries, hiddenimports = collect_all('jaraco')

# 收集pkg_resources及其子模块
pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all('pkg_resources')
datas += pkg_datas
binaries += pkg_binaries
hiddenimports += pkg_hiddenimports

# 确保明确包含所有已知的jaraco子模块
hiddenimports += [
    'jaraco',
    'jaraco.text',
    'jaraco.functools',
    'jaraco.classes',
    'jaraco.collections',
    'jaraco.context',
    'jaraco.itertools',
    'jaraco.structs',
    'more_itertools',
    'importlib_resources',
    'importlib_metadata',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
    'packaging.markers',
    'packaging.tags',
]

# 复制元数据，对pkg_resources很重要
datas += copy_metadata('jaraco.text')
datas += copy_metadata('jaraco.functools')
datas += copy_metadata('jaraco.classes')
datas += copy_metadata('pkg_resources')
""")

    # 创建自定义的运行时钩子，用于预先导入jaraco
    with open("pre_import_jaraco.py", "w") as f:
        f.write("""
# 此运行时钩子将在PyInstaller打包的应用程序启动时执行
# 它将预先导入jaraco包，确保它在pkg_resources需要它之前已经可用

import os
import sys
import importlib
import site

# 确保_MEIPASS目录在sys.path中的最前面
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, bundle_dir)

# 在Windows上，确保_MEIPASS在PATH环境变量中
if sys.platform.startswith('win'):
    os.environ['PATH'] = bundle_dir + os.pathsep + os.environ.get('PATH', '')

# 预加载jaraco包和相关模块
try:
    print("预加载jaraco模块...")
    import jaraco
    import jaraco.text
    import jaraco.functools
    import jaraco.classes
    import jaraco.collections
    print("jaraco模块加载成功")
except ImportError as e:
    print(f"无法导入jaraco模块: {e}")
    # 尝试查找模块位置
    print("系统路径:")
    for p in sys.path:
        print(f"  {p}")
    
    # 尝试直接导入jaraco子模块
    try:
        sys.path.extend([
            os.path.join(bundle_dir, 'jaraco'),
            os.path.join(bundle_dir, 'pkg_resources', '_vendor', 'jaraco'),
        ])
        print("修改路径后再次尝试导入...")
        import jaraco
        print(f"jaraco模块位置: {jaraco.__file__}")
    except ImportError as e2:
        print(f"二次导入尝试也失败: {e2}")
""")

    # 修改pkg_resources的行为，避免使用jaraco
    with open("disable_pkg_resources_extern.py", "w") as f:
        f.write("""
# 此钩子修改pkg_resources的行为，避免使用jaraco

def patch_pkg_resources():
    '''尝试修改pkg_resources以避免jaraco依赖'''
    try:
        import pkg_resources
        
        # 如果extern模块已经存在，尝试修改其导入行为
        if hasattr(pkg_resources, 'extern'):
            original_load_module = pkg_resources.extern.load_module
            
            def patched_load_module(module_name):
                if module_name.startswith('jaraco'):
                    # 尝试直接从真实路径导入jaraco，而不是通过extern
                    import importlib
                    try:
                        return importlib.import_module(module_name)
                    except ImportError:
                        print(f"无法直接导入 {module_name}，尝试使用原始加载方法")
                return original_load_module(module_name)
            
            # 替换加载方法
            pkg_resources.extern.load_module = patched_load_module
            print("已修补pkg_resources.extern.load_module")
    except Exception as e:
        print(f"修补pkg_resources失败: {e}")

# 在主脚本开始执行前调用此函数
patch_pkg_resources()
""")

def build_exe():
    """
    使用PyInstaller打包应用为可执行文件
    """
    print_banner("开始打包Git命令监控应用")
    
    # 获取当前工作目录的绝对路径
    current_dir = os.path.abspath(".")
    
    # 安装或升级PyInstaller
    print("安装最新版本的PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"], check=True)
    except Exception as e:
        print(f"安装PyInstaller时出错: {e}")
        print("继续使用现有版本...")
    
    # 安装必需的依赖项
    print("安装必要的依赖...")
    try:
        # 安装或更新jaraco相关包
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "jaraco.text", "jaraco.functools", "jaraco.classes", "jaraco.collections"], check=True)
        # 安装setuptools以解决版本检测问题
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools"], check=True)
        # 安装其他可能缺少的依赖
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "importlib_resources", "importlib_metadata", "more_itertools"], check=True)
        
        # 获取jaraco的安装位置
        print("检查jaraco包的安装位置...")
        try:
            import jaraco
            print(f"jaraco包已安装于: {jaraco.__file__}")
        except ImportError:
            print("警告: 无法导入jaraco模块，尝试安装它...")
            subprocess.run([sys.executable, "-m", "pip", "install", "jaraco"], check=True)
            
        # 安装完成后验证包的可用性
        subprocess.run([sys.executable, "-c", "import jaraco.text, jaraco.functools, jaraco.classes, pkg_resources; print('所有必要的包已正确安装')"], check=True)
    except Exception as e:
        print(f"安装依赖项时出错: {e}")
        print("继续尝试打包，但可能会失败...")
    
    # 确保icons文件夹存在
    if not os.path.exists("icons"):
        os.makedirs("icons")
    
    # 如果图标不存在，则创建
    if not os.path.exists("app_icon.png"):
        print("应用图标不存在，正在创建...")
        subprocess.run([sys.executable, "create_icon.py"], check=True)
    
    # 检查 tray_app.py 文件是否存在
    tray_app_path = os.path.join(current_dir, "tray_app.py")
    if not os.path.exists(tray_app_path):
        print(f"错误：找不到 tray_app.py 文件。预期路径：{tray_app_path}")
        return
    
    # 清理旧的构建文件
    print("清理旧的构建文件...")
    safe_remove_path("dist/GitCommandMonitor")
    safe_remove_path("build")
    safe_remove_path("__pycache__")
    safe_remove_path("GitCommandMonitor.spec")
    
    # 创建自定义钩子
    print("创建自定义钩子...")
    create_custom_hooks()
    
    # 拷贝jaraco包到当前目录，确保PyInstaller能找到它
    print("拷贝jaraco包到当前目录...")
    try:
        import jaraco
        jaraco_dir = os.path.dirname(jaraco.__file__)
        target_dir = os.path.join(current_dir, "jaraco")
        
        if os.path.exists(target_dir):
            safe_remove_path(target_dir)
        
        shutil.copytree(jaraco_dir, target_dir)
        print(f"成功将jaraco包从 {jaraco_dir} 拷贝到 {target_dir}")
    except Exception as e:
        print(f"拷贝jaraco包时出错: {e}")
    
    print("开始构建应用...")
    
    # 使用更可靠的方式打包，专注于解决jaraco依赖问题
    try:
        # 准备PyInstaller命令
        cmd = [
            "pyinstaller",
            "--name=GitCommandMonitor",
            "--onedir",  # 使用onedir模式
            "--windowed",  # 无控制台窗口
            "--clean",
            "--noconfirm",  # 不显示确认对话框
            "--log-level=DEBUG",  # 使用DEBUG级别获取更详细的日志
            f"--icon={os.path.join(current_dir, 'app_icon.png')}",
            "--add-data", f"{os.path.join(current_dir, 'app_icon.png')};.",
            "--add-data", f"{os.path.join(current_dir, 'config.json')};.",
            "--additional-hooks-dir=.",  # 添加当前目录作为hooks目录
            "--runtime-hook=pre_import_jaraco.py",  # 添加自定义运行时钩子
            "--runtime-hook=disable_pkg_resources_extern.py",  # 添加运行时钩子修改pkg_resources行为
            
            # 确保明确包含jaraco及其子模块
            "--hidden-import=jaraco",
            "--hidden-import=jaraco.text",
            "--hidden-import=jaraco.functools",
            "--hidden-import=jaraco.classes",
            "--hidden-import=jaraco.collections",
            "--hidden-import=jaraco.context",
            "--hidden-import=jaraco.itertools",
            
            # pkg_resources及相关依赖
            "--hidden-import=pkg_resources",
            "--hidden-import=pkg_resources.extern",
            "--hidden-import=importlib_resources",
            "--hidden-import=importlib_metadata",
            "--hidden-import=more_itertools",
            
            # PyQt5相关
            "--hidden-import=PyQt5",
            "--hidden-import=PyQt5.QtCore",
            "--hidden-import=PyQt5.QtGui",
            "--hidden-import=PyQt5.QtWidgets",
            
            # 其他必要模块
            "--hidden-import=matplotlib",
            "--hidden-import=pandas",
            "--hidden-import=jinja2",
            "--hidden-import=markdown",
            "--hidden-import=numpy",
            
            "--collect-all=jaraco",  # 收集jaraco的所有模块
            "--collect-all=pkg_resources",  # 收集pkg_resources的所有模块
            
            # 添加Python路径
            "--paths=" + os.path.dirname(sys.executable),
            "--paths=" + os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages"),
            "--paths=" + current_dir,  # 添加当前目录(含复制的jaraco)
        ]
        
        # 添加site-packages中的所有路径
        for path in site.getsitepackages():
            cmd.extend(["--paths=", path])
        
        # 添加主脚本
        cmd.append(tray_app_path)
        
        print("执行命令: " + " ".join(cmd))
        subprocess.run(cmd, check=True)
        print("应用构建成功！")
    except subprocess.CalledProcessError as e:
        print(f"构建应用失败: {e}")
        print("\n尝试替代方案...")
        
        # 尝试另一种方法：将jaraco直接拷贝到目标目录
        print("尝试使用最简单的打包方式，然后手动拷贝jaraco包...")
        try:
            simple_cmd = [
                "pyinstaller",
                "--onedir",
                "--windowed",
                "--name=GitCommandMonitor",
                tray_app_path
            ]
            print("执行命令: " + " ".join(simple_cmd))
            subprocess.run(simple_cmd, check=True)
            
            # 构建完成后，手动拷贝jaraco包到目标目录
            print("手动拷贝jaraco包到目标目录...")
            import jaraco
            jaraco_dir = os.path.dirname(jaraco.__file__)
            target_dir = os.path.join("dist", "GitCommandMonitor", "jaraco")
            
            if os.path.exists(target_dir):
                safe_remove_path(target_dir)
                
            shutil.copytree(jaraco_dir, target_dir)
            print(f"成功将jaraco包拷贝到 {target_dir}")
            
            # 创建一个简单的启动脚本来设置正确的导入路径
            starter_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import runpy

# 设置正确的导入路径
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

# 导入jaraco包预先加载
try:
    import jaraco
    print(f"成功加载jaraco包: {jaraco.__file__}")
except ImportError as e:
    print(f"导入jaraco包失败: {e}")

# 运行主程序
try:
    runpy.run_module("GitCommandMonitor", run_name="__main__")
except Exception as e:
    print(f"运行应用失败: {e}")
    input("按Enter键退出...")
"""
            with open(os.path.join("dist", "GitCommandMonitor", "start_app.py"), "w") as f:
                f.write(starter_script)
                
            print("创建了启动脚本 start_app.py，可使用此脚本启动应用")
        except Exception as e2:
            print(f"替代方案也失败: {e2}")
            return
    
    # 创建配置文件
    if not os.path.exists("dist/GitCommandMonitor/config.json"):
        default_config = """{
  "storage_path": "./data",
  "log_file": "./logs/monitor.log",
  "report_path": "./reports",
  "ignored_commands": ["git diff", "git log"],
  "system_level_monitoring": true,
  "monitor_interval": 1,
  "pid_cache_ttl": 300,
  "github_records": {
    "enabled": true,
    "separate_storage": true,
    "highlight_output": true
  },
  "report": {
    "auto_generate": {
      "enabled": false,
      "daily": true,
      "weekly": true,
      "monthly": true,
      "time": "23:50"
    }
  }
}"""
        with open("dist/GitCommandMonitor/config.json", "w") as f:
            f.write(default_config)
    
    # 创建必要的目录
    for directory in ["data", "logs", "reports", "reports/charts"]:
        os.makedirs(os.path.join("dist/GitCommandMonitor", directory), exist_ok=True)
    
    # 创建README.txt
    readme_content = """Git命令监控工具

感谢您使用Git命令监控工具！

使用说明：
1. 运行GitCommandMonitor.exe启动应用
2. 应用将在系统托盘区域（右下角）显示图标
3. 右键点击图标可以生成报告、打开报告目录、设置开机自启动等
4. 应用会自动在后台监控Git命令，并将数据保存到data目录

文件夹说明：
- data: 存储Git命令记录
- logs: 存储应用日志
- reports: 存储生成的报告
- reports/charts: 存储报告图表

配置文件说明：
可以编辑config.json文件自定义工具行为。

如有问题，请联系：yourname@example.com
"""
    with open("dist/GitCommandMonitor/README.txt", "w") as f:
        f.write(readme_content)
    
    print_banner("应用构建完成")
    print(f"可执行文件已生成：{os.path.abspath('dist/GitCommandMonitor/GitCommandMonitor.exe')}")
    print("您可以将dist/GitCommandMonitor目录复制到任意位置运行。")
    print("\n注意：如果运行时仍出现jaraco相关错误，请尝试使用dist/GitCommandMonitor/start_app.py脚本启动应用。")

if __name__ == "__main__":
    build_exe() 