
# hook-pkg_resources.py
from PyInstaller.utils.hooks import collect_all

# ȷ������jaraco����������ģ��
datas, binaries, hiddenimports = collect_all('jaraco')
hiddenimports += ['jaraco', 'jaraco.text', 'jaraco.functools', 'jaraco.classes']
        