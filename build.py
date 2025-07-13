"""
Main build orchestration script.

Purpose: Handles command-line flags and calls modules to build the site.
"""

import os
import yaml

from oerforge.copyfile import copy_project_files
from oerforge.make import build_all_markdown_files, ensure_build_structure
from oerforge.scan import initialize_database, populate_build_images
from oerforge.verify import run_wcag_zoo_on_page, generate_one_markdown_report, save_report_to_build_folder

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "_config.yml")
FILES_DIR = os.path.join(PROJECT_ROOT, "build", "files")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def copy_files():
    print("[INFO] Copying project files and static assets (debug mode)...")
    try:
        copy_project_files(debug=True)
        print("[OK] Project files copied.")
    except Exception as e:
        print(f"[ERROR] Copying project files failed: {e}")

def initialize_images_db():
    print("[INFO] Initializing database and scanning build/files/assets for images...")
    initialize_database()
    populate_build_images()
    print("[OK] Database initialized and build_images table populated.")

def build_site(toc):
    print("[INFO] Creating index.html pages for folders as per toc...")
    ensure_build_structure(toc)
    print("[OK] Index.html pages created.")

    print("[INFO] Converting all markdown files in build/files to HTML...")
    build_all_markdown_files(FILES_DIR, BUILD_DIR)
    print("[OK] All markdown files converted.")

def test_wcag_on_index():
    page_path = os.path.join(BUILD_DIR, "index.html")
    browser = "chrome"
    print(f"[TEST] Running WCAG test on {page_path} with {browser}")
    result = run_wcag_zoo_on_page(page_path, browser)
    md_report = generate_one_markdown_report(result)
    report_path = save_report_to_build_folder(md_report)
    print(f"[TEST] WCAG Markdown Report saved to: {report_path}")
    print(md_report)

def main():
    config = load_config(CONFIG_PATH)
    toc = config.get("toc", [])

    copy_files()
    initialize_images_db()
    build_site(toc)

if __name__ == "__main__":
    main()
    test_wcag_on_index()