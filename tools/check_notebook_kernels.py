"""
check_notebook_kernels.py

Check all notebooks for correct kernel metadata. Exits with nonzero code if any are wrong.
"""
import sys
import argparse
from notebook_kernel_utils import check_all_notebook_kernels

def main():
    parser = argparse.ArgumentParser(description="Check all notebooks for correct kernel metadata.")
    parser.add_argument('--root', default='content/', help='Root directory to search for notebooks')
    parser.add_argument('--debug', action='store_true', help='Print debug information')
    args = parser.parse_args()
    bad = check_all_notebook_kernels(args.root, debug=args.debug)
    if bad:
        print(f"[FAIL] {len(bad)} notebook(s) have wrong kernel. See above.")
        sys.exit(1)
    else:
        print("[OK] All notebooks have correct kernel.")
        sys.exit(0)

if __name__ == "__main__":
    main()
