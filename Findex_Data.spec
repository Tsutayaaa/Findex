# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['Findex_Data.py'],
    pathex=['C:\\Users\\he\\OneDrive\\Documents\\PythonProject'],  # 指定脚本路径
    binaries=[],
    datas=[('heat_loader.py', '.'), ('beh_loader.py', '.')],      # 添加依赖文件
    hiddenimports=['numpy', 'numpy.core.multiarray', 'fuzzywuzzy'],  # 添加隐藏依赖
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Findex_Data',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Findex_Data',
)