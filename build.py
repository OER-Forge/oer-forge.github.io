from oerforge.scan import initialize_database, populate_site_info, populate_toc, read_toc_item_from_db

def main():
    initialize_database()
    populate_site_info()
    populate_toc()
    # Print a single TOC item
    item_id = 2 # Change as needed
    toc_item = read_toc_item_from_db(item_id)
    print("TOC Item:", toc_item)

if __name__ == "__main__":
    main()