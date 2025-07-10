#!/usr/bin/env python3
"""
Copy all .ipynb files from content/ (recursively) to _build/ipynb and docs/ipynb as a flat set (no subfolders).
Supports --debug and --files FILE1 FILE2 ...
"""
import os
from pathlib import Path
import shutil
import argparse
import sys

def copy_ipynb_flat(files=None, src_root="content", build_dir="_build/ipynb", docs_dir="docs/ipynb", debug=False):
    print("[DEBUG] Script started.")
    build_dir = Path(build_dir).resolve()
    docs_dir = Path(docs_dir).resolve()
    print(f"[DEBUG] Target build_dir: {build_dir}")
    print(f"[DEBUG] Target docs_dir: {docs_dir}")
    try:
        build_dir.mkdir(parents=True, exist_ok=True)
        docs_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Failed to create directories: {e}")
        sys.exit(1)
    if files:
        notebooks = [Path(f).resolve() for f in files]
        print(f"[DEBUG] Using --files: {notebooks}")
    else:
        src_root = Path(src_root).resolve()
        print(f"[DEBUG] Searching for .ipynb in: {src_root}")
        notebooks = list(src_root.rglob("*.ipynb"))
    if debug:
        print(f"[INFO] Found {len(notebooks)} notebooks to copy.")
    copied = 0
    for nb in notebooks:
        if not nb.exists():
            print(f"[WARN] Notebook not found: {nb}")
            continue
        dest_build = build_dir / nb.name
        try:
            shutil.copy2(nb, dest_build)
            if debug:
                print(f"[OK] Copied {nb} -> {dest_build}")
        except Exception as e:
            print(f"[ERROR] Failed to copy {nb} to {dest_build}: {e}")
            continue
        dest_docs = docs_dir / nb.name
        try:
            shutil.copy2(dest_build, dest_docs)
            if debug:
                print(f"[OK] Published {dest_build} -> {dest_docs}")
            copied += 1
        except Exception as e:
            print(f"[ERROR] Failed to copy {dest_build} to {dest_docs}: {e}")
    print(f"[DEBUG] Script finished. {copied} notebooks published.")

if __name__ == "__main__":
    print("[DEBUG] __main__ block reached.")
    parser = argparse.ArgumentParser(description="Copy .ipynb files from content/ to _build/ipynb and docs/ipynb (flat)")
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--files', nargs='+', help='Only copy the specified notebook files')
    args = parser.parse_args()
    copy_ipynb_flat(files=args.files, debug=args.debug)