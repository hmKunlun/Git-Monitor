
# ������ʱ���ӽ���PyInstaller�����Ӧ�ó�������ʱִ��
# ����Ԥ�ȵ���jaraco����ȷ������pkg_resources��Ҫ��֮ǰ�Ѿ�����

import os
import sys
import importlib
import site

# ȷ��_MEIPASSĿ¼��sys.path�е���ǰ��
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, bundle_dir)

# ��Windows�ϣ�ȷ��_MEIPASS��PATH����������
if sys.platform.startswith('win'):
    os.environ['PATH'] = bundle_dir + os.pathsep + os.environ.get('PATH', '')

# Ԥ����jaraco�������ģ��
try:
    print("Ԥ����jaracoģ��...")
    import jaraco
    import jaraco.text
    import jaraco.functools
    import jaraco.classes
    import jaraco.collections
    print("jaracoģ����سɹ�")
except ImportError as e:
    print(f"�޷�����jaracoģ��: {e}")
    # ���Բ���ģ��λ��
    print("ϵͳ·��:")
    for p in sys.path:
        print(f"  {p}")
    
    # ����ֱ�ӵ���jaraco��ģ��
    try:
        sys.path.extend([
            os.path.join(bundle_dir, 'jaraco'),
            os.path.join(bundle_dir, 'pkg_resources', '_vendor', 'jaraco'),
        ])
        print("�޸�·�����ٴγ��Ե���...")
        import jaraco
        print(f"jaracoģ��λ��: {jaraco.__file__}")
    except ImportError as e2:
        print(f"���ε��볢��Ҳʧ��: {e2}")
