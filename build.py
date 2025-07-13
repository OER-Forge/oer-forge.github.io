"""
Main build orchestration script.

Purpose: Handles command-line flags and calls modules to build the site.
"""

from oerforge.copyfile import copy_project_files
from oerforge.make import run_make

def main():
    """
    Main entry point: Only copy project files and static assets, with debug logging.
    """
    print("[INFO] Copying project files and static assets (debug mode)...")
    try:
        copy_project_files(debug=True)
        print("[OK] Project files copied.")
    except Exception as e:
        print(f"[ERROR] Copying project files failed: {e}")

    print("[INFO] Generating HTML webpages from markdown...")
    try:
        run_make(debug=True)
        print("[OK] Webpages generated.")
    except Exception as e:
        print(f"[ERROR] Generating webpages failed: {e}")

if __name__ == "__main__":
    main()