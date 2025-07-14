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

    # Test: Run batch conversion and validate all TOC-referenced files are copied
    print("\n[TEST] Running batch conversion for all TOC-referenced files...")
    from oerforge.convert import batch_convert_all_content
    batch_convert_all_content()

    # Validate files copied
    import yaml
    import os
    with open("_config.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    toc = config.get("toc", [])

    def walk_toc_all_files(items):
        files = []
        for item in items:
            file_path = item.get("file")
            if file_path:
                files.append(file_path)
            children = item.get("children", [])
            if children:
                files.extend(walk_toc_all_files(children))
        return files

    all_files = walk_toc_all_files(toc)
    missing = []
    for file_path in all_files:
        build_path = os.path.join("build/files", file_path)
        if not os.path.exists(build_path):
            missing.append(build_path)
    if missing:
        print("[TEST][FAIL] Missing files in build/files:")
        for m in missing:
            print("  ", m)
    else:
        print("[TEST][PASS] All TOC-referenced files copied to build/files/ correctly.")

if __name__ == "__main__":
    test_full_scan_and_admin()

