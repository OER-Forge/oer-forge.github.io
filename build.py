from oerforge.scan import (
    initialize_database,
    populate_site_info,
    populate_toc,
    populate_page_info_from_config,
    print_table,
    verify_toc_page_link
)

def main():
    # Step 1: Initialize the database
    initialize_database()
    print("[INFO] Database initialized.")

    # Step 2: Populate site info
    populate_site_info()
    print("[INFO] Site info populated.")

    # Step 3: Populate TOC
    populate_toc()
    print("[INFO] TOC populated.")

    # Step 4: Populate page info (links pages to TOC)
    populate_page_info_from_config()
    print("[INFO] Page info populated.")

    # Step 5: Print tables for inspection
    # print("\n[INFO] Site Table:")
    # print_table("site")
    # print("\n[INFO] TOC Table:")
    # print_table("toc")
    print("\n[INFO] Page Table:")
    print_table("page")

    # # Step 6: Verify page-to-TOC links
    # print("\n[INFO] Verifying page-to-TOC links:")
    # verify_toc_page_link()

if __name__ == "__main__":
    main()