
from oerforge.db_utils import initialize_database, pretty_print_table
from oerforge.scan import scan_toc_and_populate_db

def test_full_scan_and_admin():
    print("[TEST] Initializing database...")
    initialize_database()

    print("[TEST] Running TOC-driven scan and DB population...")
    scan_toc_and_populate_db("_config.yml")

    print("\n[DB TABLE: content]")
    pretty_print_table('content')

    print("\n[TEST] Exporting DB tables to HTML admin pages...")
    from oerforge_admin.export_db_html import export_all_tables_to_html, copy_static_assets_to_admin
    admin_output_dir = "build/admin/"
    export_all_tables_to_html(admin_output_dir)
    copy_static_assets_to_admin(admin_output_dir)
    print(f"[TEST] Admin HTML pages generated in {admin_output_dir}")

if __name__ == "__main__":
    test_full_scan_and_admin()

