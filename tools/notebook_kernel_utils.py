"""
notebook_kernel_utils.py

Utility functions for fixing and checking Jupyter notebook kernels in a project.
"""
import os
import json
import sys
import glob

KERNEL_NAME = "open-physics-ed"
KERNEL_DISPLAY_NAME = "Python (.venv)"
PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def fix_notebook_kernel(path, debug=False):
    try:
        with open(path, 'r', encoding='utf-8') as f:
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
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        if debug:
            print(f"[OK] Fixed kernel in {path}")
        return True
    except Exception as e:
        if debug:
            print(f"[ERROR] Could not fix kernel in {path}: {e}")
        return False

def fix_all_notebook_kernels(root_dir, debug=False):
    """Fix all .ipynb files under root_dir recursively."""
    files = glob.glob(os.path.join(root_dir, "**", "*.ipynb"), recursive=True)
    if debug:
        print(f"[INFO] Found {len(files)} notebooks in {root_dir}")
    count = 0
    for nb_path in files:
        if fix_notebook_kernel(nb_path, debug=debug):
            count += 1
    if debug:
        print(f"[INFO] Fixed {count} notebooks.")
    return count

def check_notebook_kernel(path, debug=False):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        ks = nb.get('metadata', {}).get('kernelspec', {})
        if ks.get('name') != KERNEL_NAME:
            if debug:
                print(f"[WARN] Wrong kernel in {path}: {ks}")
            return False
        return True
    except Exception as e:
        if debug:
            print(f"[ERROR] Could not check kernel in {path}: {e}")
        return False

def check_all_notebook_kernels(root_dir, debug=False):
    files = glob.glob(os.path.join(root_dir, "**", "*.ipynb"), recursive=True)
    bad = []
    for nb_path in files:
        if not check_notebook_kernel(nb_path, debug=debug):
            bad.append(nb_path)
    if debug:
        if bad:
            print(f"[FAIL] {len(bad)} notebooks have wrong kernel:")
            for b in bad:
                print(f"  - {b}")
        else:
            print(f"[OK] All notebooks have correct kernel.")
    return bad
