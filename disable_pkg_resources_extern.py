
# �˹����޸�pkg_resources����Ϊ������ʹ��jaraco

def patch_pkg_resources():
    '''�����޸�pkg_resources�Ա���jaraco����'''
    try:
        import pkg_resources
        
        # ���externģ���Ѿ����ڣ������޸��䵼����Ϊ
        if hasattr(pkg_resources, 'extern'):
            original_load_module = pkg_resources.extern.load_module
            
            def patched_load_module(module_name):
                if module_name.startswith('jaraco'):
                    # ����ֱ�Ӵ���ʵ·������jaraco��������ͨ��extern
                    import importlib
                    try:
                        return importlib.import_module(module_name)
                    except ImportError:
                        print(f"�޷�ֱ�ӵ��� {module_name}������ʹ��ԭʼ���ط���")
                return original_load_module(module_name)
            
            # �滻���ط���
            pkg_resources.extern.load_module = patched_load_module
            print("���޲�pkg_resources.extern.load_module")
    except Exception as e:
        print(f"�޲�pkg_resourcesʧ��: {e}")

# �����ű���ʼִ��ǰ���ô˺���
patch_pkg_resources()
