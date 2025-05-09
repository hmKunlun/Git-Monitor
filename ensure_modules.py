
import os
import sys
import importlib
import site

# 确保DLL路径添加到搜索路径
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
sys.path.append(bundle_dir)
os.environ['PATH'] = bundle_dir + os.pathsep + os.environ['PATH']

# 预加载关键模块
try:
    import pkg_resources
    import jaraco
    import jaraco.text
    import jaraco.functools
    import jaraco.classes
except ImportError as e:
    print(f"预加载模块时出错: {e}")
