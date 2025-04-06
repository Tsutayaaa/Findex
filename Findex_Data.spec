# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['./src/Findex_Data.py'],  # 你的主脚本
    pathex=['/Users/shulei/PycharmProjects/Findex/src'],  # 这里添加源代码路径
    binaries=[],
    datas=[],
    hiddenimports=['loader','numpy','numpy.core.multiarray'],  # 确保 loader 是隐藏导入的模块
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
    console=False,
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
    distpath='/Users/shulei/PycharmProjects/Findex/dist'
)

app = BUNDLE(
    coll,
    name='Findex_Data.app',
    icon=None,
    bundle_identifier=None,
)