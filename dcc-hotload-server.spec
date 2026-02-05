# dcc-hotload-server.spec
# -*- mode: python ; coding: utf-8 -*-
import sys

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Collect hooks inside dcc_hotload_server/hooks
datas = collect_data_files(
    "dcc_hotload_server",
    includes=["hooks/*.py"]
)

hiddenimports = collect_submodules("dcc_hotload_server")

# datas = collect_data_files("dcc_hotload_server.hooks", include_py_files=True)

a = Analysis(
    ["dcc_hotload_server/main.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f"dcc-hotload-server-{sys.platform}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # set False if you want GUI
)