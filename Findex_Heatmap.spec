# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['./src/Findex_Heatmap.py'],  # 你的主脚本
    pathex=['/Users/shulei/PycharmProjects/Findex/src'],  # 这里添加源代码路径
    binaries=[],
    datas=[],
    hiddenimports=['loader'],  # 确保 loader 是隐藏导入的模块
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
    name='Findex_Heatmap',  # 更改为 Findex_Heatmap
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='Findex_Heatmap',  # 更改为 Findex_Heatmap
    distpath='/Users/shulei/PycharmProjects/Findex/dist'
)

app = BUNDLE(
    coll,
    name='Findex_Heatmap.app',  # 更改为 Findex_Heatmap.app
    icon=None,
    bundle_identifier=None,
)