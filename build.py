"""
build.py: Asset database CLI for pages/files only.
"""

import os
from oerforge.scan import initialize_database, scan_and_populate_files_db, print_table

def main():
    print("[DB] Initializing asset database...")
    initialize_database()
    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content')
    print(f"[DB] Scanning and populating files from: {content_dir}")
    scan_and_populate_files_db(content_dir)
    print("[DB] Files table:")
    print_table('files')
    print("[DB] Pages_Files table:")
    print_table('pages_files')

if __name__ == "__main__":
    main()