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

    # Minimal test for image handling workflow
    print("\n[TEST] Running image handling workflow for a sample content record...")
    import sqlite3
    from oerforge.convert import handle_images_for_markdown
    conn = sqlite3.connect("db/sqlite.db")
    cursor = conn.cursor()
    cursor.execute("SELECT source_path FROM content WHERE source_path LIKE 'content/sample/notebooks/%' LIMIT 1")
    row = cursor.fetchone()
    if row:
        content_record = {"source_path": row[0]}
        handle_images_for_markdown(content_record, conn)
        print(f"[TEST] Image handling completed for {content_record['source_path']}")
    else:
        print("[TEST] No sample notebook found in content table for image handling test.")
    conn.close()

if __name__ == "__main__":
    test_full_scan_and_admin()

