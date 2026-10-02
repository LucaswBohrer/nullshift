# -*- coding: utf-8 -*-
"""PyInstaller build spec for NULL//SHIFT (one-dir, D007)."""
import os

block_cipher = None
ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

a = Analysis(
    ["src/nullshift/__main__.py"],
    pathex=[os.path.join(ROOT, "src")],
    binaries=[],
    datas=[
        (os.path.join(ROOT, "data"), "data"),
        (os.path.join(ROOT, "assets"), "assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="NULLSHIFT",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="NULLSHIFT",
)
