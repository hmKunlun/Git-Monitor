
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
