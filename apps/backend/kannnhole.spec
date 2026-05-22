# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Analysis collects all imports, binaries, and static asset folders
a = Analysis(
    ['kannnhole.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../frontend/dist', 'frontend'),
        ('../../packages/agent/installer_template.sh', 'agent'),
        ('../../packages/agent/ktmc', 'agent'),
        ('../../packages/agent/bin/frp/frpc', 'agent/bin/frp'),
        ('bin/frp/frps', 'bin/frp'),
    ],
    hiddenimports=[
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.loops.uvloop',
        'uvicorn.loops.iocp',
        'uvicorn.loops.win32',
        'uvicorn.loops.select',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http',
        'uvicorn.protocols',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.lifespan',
        'starlette.middleware.sessions',
        'fastapi.staticfiles',
        'psycopg2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE bundles everything into a single standalone executable file
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='kannnhole',
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
)
