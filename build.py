"""
build.py: Complete asset DB and admin export workflow.
"""

import os
import subprocess
from oerforge.scan import initialize_database, scan_and_populate_files_db, print_table
from oerforge_admin.export_db_html import export_all_tables_to_html, copy_static_assets_to_admin
from oerforge_admin.view_db import insert_autobuilt_page

def main():
    print("[DB] Initializing asset database and schema...")
    initialize_database()

    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content')
    print(f"[DB] Scanning and populating files from: {content_dir}")
    scan_and_populate_files_db(content_dir)

    print("[DB] CLI output from view_db.py --all:")
    admin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oerforge_admin', 'view_db.py')
    result = subprocess.run(['python3', admin_path, '--all'], capture_output=True, text=True)
    print(result.stdout)

    # --- Export static admin pages and assets ---
    print("[ADMIN] Exporting static HTML tables to build/admin ...")
    admin_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', 'admin')
    export_all_tables_to_html(admin_output_dir)
    copy_static_assets_to_admin(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build'))
    print(f"[ADMIN] Static admin pages and assets exported to: {admin_output_dir}")

    # --- Insert admin page records into DB ---
    for table in ['files_table.html', 'pages_files_table.html']:
        output_path = os.path.join(admin_output_dir, table)
        insert_autobuilt_page(output_path)
    print("[DB] Admin page records inserted into pages table.")

if __name__ == "__main__":
    main()