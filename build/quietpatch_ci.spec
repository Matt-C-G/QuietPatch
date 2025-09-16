# PyInstaller spec for CI builds (GUI + CLI)
# Simplified for CI environment without complex path dependencies

block_cipher = None

# CLI build
a_cli = Analysis(
    ['qp_cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('catalog', 'catalog'),
        ('policies', 'policies'),
        ('config', 'config'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz_cli = PYZ(a_cli.pure, a_cli.zipped_data, cipher=block_cipher)
exe_cli = EXE(pyz_cli, a_cli.scripts, name='quietpatch', console=True)

# GUI build
a_gui = Analysis(
    ['gui/wizard.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('catalog', 'catalog'),
        ('policies', 'policies'),
        ('config', 'config'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz_gui = PYZ(a_gui.pure, a_gui.zipped_data, cipher=block_cipher)
exe_gui = EXE(pyz_gui, a_gui.scripts, name='QuietPatchWizard', console=False)
