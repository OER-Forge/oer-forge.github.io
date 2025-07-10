"""
fix_notebook_kernels.py

Batch update all .ipynb notebooks in the repo to use the local Jupyter kernel for the .venv environment.
- Sets kernelspec name to 'open-physics-ed' and display_name to 'Python (.venv)'.
- Optionally updates language_info to match the current Python version.

Usage:
    python fix_notebook_kernels.py [notebook_path ...]
    # If no paths are given, will scan content/ for all .ipynb files.
"""
import sys
import json
import glob
import os
import platform

KERNEL_NAME = "open-physics-ed"
KERNEL_DISPLAY_NAME = "Python (.venv)"
PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def fix_kernel(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    if 'metadata' not in nb:
        nb['metadata'] = {}
    nb['metadata']['kernelspec'] = {
        "name": KERNEL_NAME,
        "display_name": KERNEL_DISPLAY_NAME,
        "language": "python"
    }
    nb['metadata']['language_info'] = {
        "name": "python",
        "version": PYTHON_VERSION
    }
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"[OK] Updated kernel in {notebook_path}")


def main():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = glob.glob("content/**/*.ipynb", recursive=True)
    if not files:
        print("No notebooks found.")
        return
    for nb_path in files:
        fix_kernel(nb_path)

if __name__ == "__main__":
    main()
