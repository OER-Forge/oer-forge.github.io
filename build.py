from oerforge.convert import ipynb_to_md

def main():
    initialize_database()
    print("[INFO] Database initialized.")

    populate_site_info()
    print("[INFO] Site info populated.")

    populate_toc()
    print("[INFO] TOC populated.")

    populate_page_info_from_config()
    print("[INFO] Page info populated.")

    scan_all_images()
    print("[INFO] Starting image scan")
    print_table('page_images')

    # Test ipynb_to_md after database is populated
    test_ipynb = "content/notebooks/week1/example.ipynb"  # Use a real notebook path
    try:
        md_path = ipynb_to_md(test_ipynb, None)
        print(f"[TEST] Converted to markdown: {md_path}")
    except Exception as e:
        print(f"[TEST] Conversion failed: {e}")

if __name__ == "__main__":
    main()