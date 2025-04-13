# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SentinelPC_cli_v2.py'],
    pathex=[],
    binaries=[],
    datas=[('config/*.ini', 'config')],
    hiddenimports=['config_manager_v2', 'performance_optimizer_v2'],
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
    a.binaries,
    a.datas,
    [],
    name='sysopt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['favicon_ico\\favicon.ico'],
)
