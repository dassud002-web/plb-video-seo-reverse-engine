# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None
project_root = Path(SPECPATH)

candidate_datas = [
    (project_root / "templates", "templates"),
    (project_root / "static", "static"),
    (project_root / "story_forge" / "templates", "story_forge/templates"),
    (project_root / "story_forge" / "static", "story_forge/static"),
    (project_root / "studio" / "templates", "studio/templates"),
    (project_root / "studio" / "static", "studio/static"),
    (project_root / "scripts", "scripts"),
    (project_root / "input", "input"),
    (project_root / "story_forge" / "models", "story_forge/models"),
]

added_datas = []
for src, dst in candidate_datas:
    if src.exists():
        added_datas.append((str(src), dst))

hidden_imports = [
    "flask",
    "jinja2",
    "werkzeug",
    "werkzeug.serving",
    "cv2",
    "numpy",
    "sqlite3",
    "yaml",
    "scripts",
    "scripts.video_seo_reverse_engineer",
    "story_forge",
    "story_forge.app",
    "story_forge.engine.character_universe",
    "story_forge.engine.relationship_engine",
    "story_forge.engine.story_genome",
    "story_forge.engine.story_worlds",
    "story_forge.engine.universe_engine",
    "story_forge.engine.quality_engine",
    "story_forge.engine.production_pipeline",
    "story_forge.engine.prompt_compiler",
    "story_forge.engine.doc_registry",
    "story_forge.engine.vision_pipeline",
    "story_forge.engine.video_story_extractor",
    "story_forge.engine.story_dna",
    "story_forge.engine.story_generator",
    "story_forge.engine.expansion_engine",
    "story_forge.engine.lineage_engine",
    "story_forge.engine.evidence",
    "story_forge.diagnostics",
    "story_forge.diagnostics.activity_logger",
    "story_forge.storage.db",
    "story_forge.exports.exporter",
    "studio.app",
]

a = Analysis(
    [str(project_root / "desktop_app.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=added_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "pytest", "IPython"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PLB-Studio',
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
    icon=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PLB-Studio',
)
