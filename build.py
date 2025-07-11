from oerforge.scan import *

def main():
    initialize_database()
    populate_site_info()
    populate_toc()
    print("Site table:")
    print_table("site")
    print("\nTOC table:")
    print_table("toc")
    # Optionally, read and print a single TOC item by ID
    toc_item = read_toc_item_from_db(1)  # Change 1 to any valid toc_id
    print("\nSingle TOC item (toc_id=1):")
    print(toc_item)

if __name__ == "__main__":
    main()