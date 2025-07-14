# build-test.py

from oerforge.db_utils import initialize_database
from oerforge.scan import scan_toc_and_populate_db
from oerforge.convert import batch_convert_all_content

def main():
    print("Step 1: Initializing database...")
    initialize_database()
    print("Step 2: Scanning TOC and populating database...")
    scan_toc_and_populate_db('_config.yml')
    print("Step 3: Batch converting all content (files, images, links)...")
    batch_convert_all_content()
    print("Build test complete.")

if __name__ == "__main__":
    main()