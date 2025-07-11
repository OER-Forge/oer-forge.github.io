from oerforge.scan import *

def get_last_toc_id():
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM toc ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def main():
    initialize_database()
    populate_site_info()
    populate_toc()

    # Print last item before insert
    last_id = get_last_toc_id()
    print("Last TOC item before insert:", read_toc_item_from_db(last_id) if last_id else "None")

    # Insert a new TOC item
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    new_toc_item = {
        "filename": "content/new_item.md",
        "title": "New Item",
        "filetype": "md",
        "level": 0,
        "automated_build": 0
    }
    write_toc_item_to_db(cursor, new_toc_item)
    conn.commit()
    conn.close()

    # Print last item after insert
    last_id = get_last_toc_id()
    print("Last TOC item after insert:", read_toc_item_from_db(last_id))

if __name__ == "__main__":
    main()