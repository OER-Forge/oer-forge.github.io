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
    # print("\n[INFO] Page Table:")
    # print_table("page")

    # Step 6: Demonstrate extracting images from a single notebook file
    from oerforge.scan import extract_image_info_from_ipynb
    # Example: Use a known notebook and page_id (update these as needed)
    ipynb_path = "content/notebooks/1_mechanics/dynamical_systems/activity-duffing.ipynb"
    page_id = 1  # Replace with the actual page_id for this notebook
    print(f"[INFO] Extracting images from {ipynb_path} for page_id {page_id}...")
    extract_image_info_from_ipynb(ipynb_path, page_id)
    print("[INFO] Image extraction complete.")
    print("\n[INFO] Page Images Table:")
    print_table("page_images")

    # # Step 6: Verify page-to-TOC links
    # print("\n[INFO] Verifying page-to-TOC links:")
    # verify_toc_page_link()

if __name__ == "__main__":
    main()