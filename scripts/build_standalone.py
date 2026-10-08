#!/usr/bin/env python3
"""
PLB Creator Studio — Standalone Executable Builder
===================================================
Automates PyInstaller compilation to produce a self-contained
Windows desktop distribution under dist/PLB-Studio/.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

project_root = Path(__file__).resolve().parent.parent

def build():
    print("=" * 70)
    print(" 🛠️  BUILDING PLB CREATOR STUDIO STANDALONE EXECUTABLE")
    print("=" * 70)
    print("Project Root:", project_root)

    # 1. Verify PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller version {PyInstaller.__version__} detected")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Clean previous build artifacts
    build_dir = project_root / "build"
    dist_dir = project_root / "dist" / "PLB-Studio"
    spec_file = project_root / "plb_studio.spec"

    if build_dir.exists():
        print("Cleaning previous build directory...")
        shutil.rmtree(build_dir, ignore_errors=True)
    if dist_dir.exists():
        print("Cleaning previous distribution directory...")
        shutil.rmtree(dist_dir, ignore_errors=True)

    # 3. Execute PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        str(spec_file)
    ]
    print(f"\nRunning PyInstaller: {' '.join(cmd)}\n")
    proc = subprocess.run(cmd, cwd=str(project_root))

    if proc.returncode != 0:
        print("\n❌ Build failed with exit code %d" % proc.returncode)
        sys.exit(proc.returncode)

    exe_path = dist_dir / "PLB-Studio.exe"
    if exe_path.exists():
        size_mb = round(exe_path.stat().st_size / (1024 * 1024), 2)
        print("\n" + "=" * 70)
        print(" 🎉 BUILD SUCCESSFUL!")
        print("=" * 70)
        print(f" Executable: {exe_path}")
        print(f" Size:       {size_mb} MB")
        print(f" Folder:     {dist_dir}")
        print("\nCreators can run PLB Creator Studio directly via:")
        print(f" -> {exe_path}")
        print("=" * 70)
    else:
        print("\n⚠️ Build finished, but expected executable was not found at:", exe_path)

if __name__ == "__main__":
    build()
