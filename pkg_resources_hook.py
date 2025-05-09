
# hook-pkg_resources.py
from PyInstaller.utils.hooks import collect_all

# 确保导入jaraco及其所有子模块
datas, binaries, hiddenimports = collect_all('jaraco')
hiddenimports += ['jaraco', 'jaraco.text', 'jaraco.functools', 'jaraco.classes']
        