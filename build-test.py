from oerforge.db_utils import initialize_database
from oerforge.scan import batch_read_files


# --- Batch file reading test ---
def test_batch_read_files():
    print("[TEST] Initializing database...")
    initialize_database()

    # Use markdown, notebook, and docx files for the test
    file_paths = [
        "content/about.md",
        "content/sample/notebooks/01_notes.ipynb",
        "content/sample/activity-metropolis.docx",
        "content/sample/notes-phase_space.docx"
    ]
    print(f"[TEST] Reading files: {file_paths}")
    contents = batch_read_files(file_paths)
    for path, content in contents.items():
        print(f"\n[CONTENTS of {path}]:\n{content}\n")



if __name__ == "__main__":
    print("[TEST] Initializing database...")
    initialize_database()

    # --- TOC-driven scan and DB population test ---
    print("[TEST] Running TOC-driven scan and DB population...")
    from oerforge.scan import scan_toc_and_populate_db
    scan_toc_and_populate_db("_config.yml")

    # Print DB tables after TOC-driven scan
    from oerforge.db_utils import pretty_print_table
    print("\n[DB TABLE: files]")
    pretty_print_table('files')
    print("\n[DB TABLE: content]")
    pretty_print_table('content')
    print("\n[DB TABLE: pages_files]")
    pretty_print_table('pages_files')
    print("\n[DB TABLE: site_info]")
    pretty_print_table('site_info')

    # --- Export DB tables to HTML admin pages ---
    print("\n[TEST] Exporting DB tables to HTML admin pages...")
    from oerforge_admin.export_db_html import export_all_tables_to_html, copy_static_assets_to_admin
    admin_output_dir = "build/admin/"
    export_all_tables_to_html(admin_output_dir)
    copy_static_assets_to_admin(admin_output_dir)
    print(f"[TEST] Admin HTML pages generated in {admin_output_dir}")

