from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import PyInstaller.__main__


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build" / "backend"
DIST_DIR = BUILD_DIR
WORK_DIR = BUILD_DIR / "work"
SPEC_DIR = BUILD_DIR / "spec"
EXE_NAME = "librarium-backend"


def _clean_previous_build() -> None:
    exe_name = f"{EXE_NAME}.exe" if os.name == "nt" else EXE_NAME
    target = DIST_DIR / exe_name
    if target.exists():
        target.unlink()
    for path in (WORK_DIR, SPEC_DIR):
        if path.exists():
            shutil.rmtree(path)


def main() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    _clean_previous_build()

    sep = ";" if os.name == "nt" else ":"
    PyInstaller.__main__.run([
        "--noconfirm",
        "--clean",
        "--onefile",
        f"--name={EXE_NAME}",
        f"--distpath={DIST_DIR}",
        f"--workpath={WORK_DIR}",
        f"--specpath={SPEC_DIR}",
        f"--add-data={ROOT / 'static'}{sep}static",
        f"--add-data={ROOT / 'templates'}{sep}templates",
        "--collect-all=pillow_heif",
        "--collect-all=markdown",
        "--collect-all=pdfplumber",
        "--collect-all=pdfminer",
        str(ROOT / "app.py"),
    ])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Backend build failed: {exc}", file=sys.stderr)
        raise