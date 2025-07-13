"""
Main build orchestration script.

Purpose: Handles command-line flags and calls modules to build the site.
"""

# from oerforge.copyfile import *
from oerforge.copyfile import copy_project_files
from oerforge.make import build_all_markdown_files
# from oerforge.make import run_make
import os

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

    # Build and convert all markdown files in build/files to build/ as HTML
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(PROJECT_ROOT, "_config.yml")
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    toc = config.get("toc", [])
    files_dir = os.path.join(PROJECT_ROOT, "build", "files")
    build_dir = os.path.join(PROJECT_ROOT, "build")

    # Initialize and build images database
    print("[INFO] Initializing database and scanning build/files/assets for images...")
    from oerforge.scan import initialize_database, populate_build_images
    initialize_database()
    populate_build_images()
    print("[OK] Database initialized and build_images table populated.")

    print("[INFO] Creating index.html pages for folders as per toc...")
    from oerforge.make import ensure_build_structure
    ensure_build_structure(toc)
    print("[OK] Index.html pages created.")
    print("[INFO] Converting all markdown files in build/files to HTML...")
    build_all_markdown_files(files_dir, build_dir)
    print("[OK] All markdown files converted.")

if __name__ == "__main__":
    main()