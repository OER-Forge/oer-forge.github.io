import os
from oerforge.db_utils import initialize_database
from oerforge.copyfile import copy_project_files
from oerforge.scan import scan_toc_and_populate_db
from oerforge.convert import batch_convert_all_content
from oerforge.make import build_all_markdown_files, setup_logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_FILES_DIR = os.path.join(PROJECT_ROOT, 'build', 'files')
BUILD_HTML_DIR = os.path.join(PROJECT_ROOT, 'build')

def run_full_workflow():
    setup_logging()
    print("Step 1: Initializing database...")
    initialize_database()
    print("Step 2: Copying project files and static assets (CSS, JS)...")
    copy_project_files()
    print(f"[DEBUG] Contents of BUILD_FILES_DIR ({BUILD_FILES_DIR}):")
    for root, dirs, files in os.walk(BUILD_FILES_DIR):
        for name in files:
            print(f"  {os.path.join(root, name)}")
    print("Step 3: Scanning TOC and populating database...")
    scan_toc_and_populate_db('_config.yml')
    print("Step 4: Batch converting all content (files, images, links)...")
    batch_convert_all_content()
    print("Step 5: Building HTML and section indexes...")
    # Debug: Show markdown files found before conversion
    from oerforge.make import find_markdown_files
    md_files = find_markdown_files(BUILD_FILES_DIR)
    print(f"[DEBUG] Markdown files found for conversion ({len(md_files)}):")
    for f in md_files:
        print(f"  {f}")
    build_all_markdown_files(BUILD_FILES_DIR, BUILD_HTML_DIR)
    print("Workflow complete. Check build/, docs/, and logs for results.")

if __name__ == "__main__":
    run_full_workflow()