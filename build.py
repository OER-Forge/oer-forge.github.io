"""
Main build orchestration script.

Purpose: Handles command-line flags and calls modules to build the site.
"""

from oerforge.copyfile import copy_project_files
# from oerforge.make import run_make
from oerforge.make import get_markdown_source_and_output_paths, load_yaml_config
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

    # Test get_markdown_source_and_output_paths after copying
    
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(PROJECT_ROOT, "_config.yml")
    config = load_yaml_config(config_path)
    toc = config.get("toc", [])
    files_dir = os.path.join(PROJECT_ROOT, "build", "files")
    build_dir = os.path.join(PROJECT_ROOT, "build")
    results = get_markdown_source_and_output_paths(toc, files_dir, build_dir)
    for src, out, entry in results:
        print(f"Source: {src}\nOutput: {out}\nTOC Entry: {entry}\n")
    print("Check the log file for missing file errors.")

if __name__ == "__main__":
    main()