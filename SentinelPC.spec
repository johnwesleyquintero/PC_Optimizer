# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\johnw\\OneDrive\\Desktop\\SentinelPC\\src\\main.py'],
    pathex=['C:\\Users\\johnw\\OneDrive\\Desktop\\SentinelPC', 'C:\\Users\\johnw\\OneDrive\\Desktop\\SentinelPC\\src'],
    binaries=[],
    datas=[('C:\\Users\\johnw\\OneDrive\\Desktop\\SentinelPC\\config', 'config'), ('C:\\Users\\johnw\\OneDrive\\Desktop\\SentinelPC\\locales', 'locales')],
    hiddenimports=['tkinter', 'PIL', 'core.performance_optimizer', 'core.sentinel_core', 'core.config_manager', 'core.environment_manager', 'core.monitoring_manager', 'core.logging_manager'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'unittest', 'pytest'],
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
    name='SentinelPC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\johnw\\OneDrive\\Desktop\\SentinelPC\\src\\gui\\assets\\icon.ico'],
)
