
import os
import sys
import importlib
import site

# ȷ��DLL·����ӵ�����·��
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
sys.path.append(bundle_dir)
os.environ['PATH'] = bundle_dir + os.pathsep + os.environ['PATH']

# Ԥ���عؼ�ģ��
try:
    import pkg_resources
    import jaraco
    import jaraco.text
    import jaraco.functools
    import jaraco.classes
except ImportError as e:
    print(f"Ԥ����ģ��ʱ����: {e}")
