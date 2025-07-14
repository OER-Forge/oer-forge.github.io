from oerforge.db_utils import initialize_database
from oerforge.copyfile import copy_project_files
from oerforge.scan import scan_toc_and_populate_db
from oerforge.convert import batch_convert_all_content
from oerforge.make import build_all_markdown_files

def main():
    print("Step 1: Initializing database...")
    initialize_database()
    print("Step 2: Copying project files and static assets (CSS, JS)...")
    copy_project_files()
    print("Step 3: Scanning TOC and populating database...")
    scan_toc_and_populate_db('_config.yml')
    print("Step 4: Batch converting all content (files, images, links)...")
    batch_convert_all_content()
    print("Step 5: Building HTML pages from markdown files...")
    build_all_markdown_files("build/files", "build")
    print("Build test complete.")

if __name__ == "__main__":
    main()