from oerforge.scan import (
    initialize_database,
    populate_site_info,
    populate_toc,
    populate_page_info_from_config,
    print_table,
    scan_all_images
)

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


if __name__ == "__main__":
    main()