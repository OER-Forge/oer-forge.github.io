from oerforge.scan import *
from oerforge.convert import copy_images_for_ipynb

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

    # Test only image copying and query notebook record
    test_ipynb = "content/notebooks/1_mechanics/lagrangian/notes-lagrangian-dynamics.ipynb"  # Use a real notebook path
    import sqlite3
    conn = sqlite3.connect('db/sqlite.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM page WHERE page_filename=?", (test_ipynb,))
    row = cursor.fetchone()
    col_names = [description[0] for description in cursor.description]
    conn.close()
    if row:
        print("[INFO] Notebook DB record:")
        for name, value in zip(col_names, row):
            print(f"  {name}: {value}")
        # Query image records for this notebook
        page_id = row[col_names.index('page_id')]
        conn = sqlite3.connect('db/sqlite.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM page_images WHERE image_page_id=?", (page_id,))
        img_rows = cursor.fetchall()
        img_col_names = [description[0] for description in cursor.description]
        conn.close()
        if img_rows:
            print("[INFO] Image DB records:")
            for img_row in img_rows:
                print("  " + ", ".join(f"{name}: {value}" for name, value in zip(img_col_names, img_row)))
        else:
            print(f"[INFO] No image records found for page_id {page_id}")
    else:
        print(f"[WARNING] No DB record found for {test_ipynb}")
    copy_images_for_ipynb(test_ipynb)

if __name__ == "__main__":
    main()