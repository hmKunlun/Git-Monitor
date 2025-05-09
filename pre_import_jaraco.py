
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
