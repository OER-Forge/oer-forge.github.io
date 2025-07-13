"""
Main build orchestration script.

Purpose: Handles command-line flags and calls modules to build the site.
"""

import os
import yaml

from oerforge.copyfile import copy_project_files
from oerforge.make import build_all_markdown_files, ensure_build_structure, copy_wcag_reports_to_docs, convert_wcag_reports_to_html, mirror_build_to_docs
from oerforge.scan import initialize_database, populate_build_images
from oerforge.verify import run_wcag_zoo_on_page, run_wcag_zoo_on_all_pages, generate_markdown_report, save_report_to_build_folder

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

def run_accessibility_checks_and_report():
    """
    Run axe-selenium-python accessibility checks on all HTML files in build/ and generate a single markdown report.
    """
    print("[WCAG] Running accessibility checks on all HTML files in build/...")
    # Find all HTML files in build/
    html_files = []
    for dirpath, dirnames, filenames in os.walk(BUILD_DIR):
        for filename in filenames:
            if filename.lower().endswith('.html'):
                html_files.append(os.path.join(dirpath, filename))
    # Define browsers to test
    browsers = ["chrome"]
    # Run accessibility checks
    results = run_wcag_zoo_on_all_pages(html_files, browsers)
    # Generate markdown report
    md_report = generate_markdown_report(results)
    report_path = save_report_to_build_folder(md_report)
    print(f"[WCAG] Accessibility Markdown Report saved to: {report_path}")
    # Optionally print summary
    print(md_report)

def main():
    config = load_config(CONFIG_PATH)
    toc = config.get("toc", [])

    copy_files()
    initialize_images_db()
    build_site(toc)
    #run_accessibility_checks_and_report()
    # Convert WCAG reports to HTML and copy to projectroot/docs/wcag-reports
    convert_wcag_reports_to_html()
    mirror_build_to_docs()

if __name__ == "__main__":
    main()