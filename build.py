"""
Main build orchestration script.

Purpose: Handles command-line flags and calls modules to build the site. This script should:
- Initialize and populate the database using scan.py routines.
- Test ipynb_to_md conversion.
- Print progress and summary.
- Log all actions and errors.
- Use type hints and clear docstrings for all functions.
"""
from oerforge.convert import ipynb_to_md
from oerforge import scan
from oerforge_admin import viewdb

def main():
    
    db_path = "db/sqlite.db"
    ipynb_path = "content/notebooks/1_mechanics/lagrangian/activity-lagrange_2.ipynb"
    output_path = None  # Not used in current ipynb_to_md signature
    output_dir = "build/admin"
    
    print("[INFO] Initializing and populating database...")
    scan.initialize_database()
    scan.populate_site_info()
    scan.populate_toc()
    scan.populate_page_info_from_config()
    scan.scan_all_images()
    print("[OK] Database initialized and populated.")

    try:
        print("[DEBUG] About to call ipynb_to_md")
        md_path = ipynb_to_md(ipynb_path, output_path)
        print(f"[OK] Markdown file created at: {md_path}")
    except Exception as e:
        print(f"[ERROR] {e}")
        
    viewdb.generate_all_table_webpages(db_path, output_dir)

if __name__ == "__main__":
    main()