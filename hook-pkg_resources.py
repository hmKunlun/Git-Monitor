
# hook-pkg_resources.py
from PyInstaller.utils.hooks import collect_all, copy_metadata

# �ռ�jaraco����������ģ��
datas, binaries, hiddenimports = collect_all('jaraco')

# �ռ�pkg_resources������ģ��
pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all('pkg_resources')
datas += pkg_datas
binaries += pkg_binaries
hiddenimports += pkg_hiddenimports

# ȷ����ȷ����������֪��jaraco��ģ��
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

# ����Ԫ���ݣ���pkg_resources����Ҫ
datas += copy_metadata('jaraco.text')
datas += copy_metadata('jaraco.functools')
datas += copy_metadata('jaraco.classes')
datas += copy_metadata('pkg_resources')
