
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
