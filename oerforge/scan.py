"""
Module: scan

Purpose: Scans _config.yml and content/ for site information, table of contents information, and page information. Writes SQLite database with three tables: site, toc, and page.
"""
import os
import sqlite3
import yaml

def initialize_database():
    """
    Initializes the SQLite database located at 'db/sqlite.db' with three tables: site, toc, and page.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(project_root, 'db')
    db_path = os.path.join(db_dir, 'sqlite.db')
    os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS page_images")
    cursor.execute("DROP TABLE IF EXISTS page")
    cursor.execute("DROP TABLE IF EXISTS toc")
    cursor.execute("DROP TABLE IF EXISTS site")

    # Create site table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS site (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_title TEXT,
            site_subtitle TEXT,
            site_url TEXT,
            site_license TEXT,
            site_logo TEXT,
            site_favicon TEXT,
            site_theme_light TEXT,
            site_theme_dark TEXT,
            site_theme_default TEXT,
            site_footer TEXT
            )
    """)

    # Create toc table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS toc (
            toc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            toc_filename TEXT,
            toc_title TEXT,
            toc_filetype TEXT,
            toc_level INTEGER,
            toc_automated_build BOOLEAN
        )
    """)

    # Create page table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS page (
            page_id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_filename TEXT,
            page_title TEXT,
            page_filetype TEXT,
            page_convert_md BOOLEAN,
            page_convert_ipynb BOOLEAN,
            page_convert_docx BOOLEAN,
            page_convert_tex BOOLEAN,
            page_convert_pdf BOOLEAN,
            page_convert_jupyter BOOLEAN,
            page_built_ok_md BOOLEAN,
            page_built_ok_ipynb BOOLEAN,
            page_built_ok_docx BOOLEAN,
            page_built_ok_tex BOOLEAN,
            page_built_ok_pdf BOOLEAN,
            page_built_ok_jupyter BOOLEAN,
            page_wcag_ok_md BOOLEAN,
            page_wcag_ok_ipynb BOOLEAN,
            page_wcag_ok_docx BOOLEAN,
            page_wcag_ok_tex BOOLEAN,
            page_wcag_ok_pdf BOOLEAN,
            page_wcag_ok_jupyter BOOLEAN,
            page_filename_md TEXT,
            page_filename_ipynb TEXT,
            page_filename_docx TEXT,
            page_filename_tex TEXT,
            page_filename_pdf TEXT,
            page_filename_jupyter TEXT,
            page_level INTEGER,  
            page_toc_id INTEGER
        )
    """)
    
    # Create page_images table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS page_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_page_id INTEGER,
            image_filename TEXT,
            FOREIGN KEY(image_page_id) REFERENCES page(page_id)
        )
    """)

    conn.commit()
    conn.close()

def populate_site_info():
    """
    Reads site information from the '_config.yml' file and writes it to the 'site' table in the SQLite database at 'db/sqlite.db'.

    Returns:
        dict: Site information parsed from the YAML configuration file.
    """
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_root, '_config.yml')
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    site_info = config.get('site', {})
    site_info['footer'] = config.get('footer', {}).get('text', '')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO site (
                site_title, site_subtitle, site_url, site_license, site_logo, site_favicon,
                site_theme_light, site_theme_dark, site_theme_default, site_footer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                site_info.get('title', ''),
                site_info.get('author', ''),
                site_info.get('github_url', ''),
                "CC BY-NC-SA 4.0",
                site_info.get('logo', ''),
                site_info.get('favicon', ''),
                site_info.get('theme', {}).get('light', ''),
                site_info.get('theme', {}).get('dark', ''),
                site_info.get('theme', {}).get('default', ''),
                site_info.get('footer', '')
            )
        )
    except sqlite3.OperationalError as e:
        print("\n[ERROR] Could not insert site info into the database.")
        print(f"[ERROR] SQLite error: {e}")
        print("[HINT] This usually means your table columns and the keys in your INSERT statement do not match.")
        print("[ACTION] Please check your database schema and the keys in your config file.")
        conn.close()
        raise
    conn.commit()
    conn.close()
    return site_info    
    
def populate_toc():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_root, '_config.yml')
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    toc_items = config.get('toc', [])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        def insert_toc_items(items, level=0):
            for item in items:
                toc_item = {
                    "toc_filename": item.get('file', None),
                    "toc_title": item.get('title', ''),
                    "toc_filetype": os.path.splitext(item.get('file', ''))[1][1:] if item.get('file', None) else None,
                    "toc_level": level,
                    "toc_automated_build": 0 if item.get('file', None) else 1
                }
                cursor.execute(
                    """
                    INSERT INTO toc (toc_filename, toc_title, toc_filetype, toc_level, toc_automated_build)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        toc_item["toc_filename"],
                        toc_item["toc_title"],
                        toc_item["toc_filetype"],
                        toc_item["toc_level"],
                        toc_item["toc_automated_build"]
                    )
                )
                if 'children' in item:
                    insert_toc_items(item['children'], level=level+1)
        insert_toc_items(toc_items, level=0)
    except sqlite3.OperationalError as e:
        print("\n[ERROR] Could not insert toc info into the database.")
        print(f"[ERROR] SQLite error: {e}")
        print("[HINT] This usually means your table columns and the keys in your INSERT statement do not match.")
        print("[ACTION] Please check your database schema and the keys in your config file.")
        conn.close()
        raise
    conn.commit()
    conn.close()

def read_toc_item_from_db(item_id):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT toc_id, toc_filename, toc_title, toc_filetype, toc_level, toc_automated_build FROM toc WHERE toc_id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "toc_id": row[0],
            "toc_filename": row[1],
            "toc_title": row[2],
            "toc_filetype": row[3],
            "toc_level": row[4],
            "toc_automated_build": row[5]
        }
    else:
        return None

def write_toc_item_to_db(cursor, toc_item):
    cursor.execute(
        """
        INSERT INTO toc (toc_filename, toc_title, toc_filetype, toc_level, toc_automated_build)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            toc_item.get('toc_filename', None),
            toc_item.get('toc_title', ''),
            toc_item.get('toc_filetype', None),
            toc_item.get('toc_level', 0),
            toc_item.get('toc_automated_build', 0)
        )
    )

def populate_page_info_from_config():
    """
    Reads page info from '_config.yml' and writes entries to the 'page' table in the SQLite database.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_root, '_config.yml')
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    toc_items = config.get('toc', [])

    # Helper to recursively collect page entries
    def collect_pages(items):
        pages = []
        for item in items:
            if 'file' in item:
                filename = item['file']
                title = item.get('title', '')
                filetype = os.path.splitext(filename)[1][1:] if filename else ''
                page = {
                    "filename": filename,
                    "title": title,
                    "filetype": filetype,
                    # You can set other fields to default values or extend as needed
                }
                pages.append(page)
            if 'children' in item:
                pages.extend(collect_pages(item['children']))
        return pages

    page_entries = collect_pages(toc_items)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for page in page_entries:
        cursor.execute(
            """
            INSERT INTO page (filename, title, filetype)
            VALUES (?, ?, ?)
            """,
            (page['filename'], page['title'], page['filetype'])
        )
    conn.commit()
    conn.close()


def read_page_item_from_db(page_id):
    """
    Reads a single page item from the 'page' table in the SQLite database at 'db/sqlite.db'.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM page WHERE id = ?", (page_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        # Get column names for mapping
        col_names = [description[0] for description in cursor.description]
        return dict(zip(col_names, row))
    else:
        return None


def write_page_item_to_db(page_item):
    """
    Writes a single page item to the 'page' table in the SQLite database at 'db/sqlite.db'.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO page (filename, title, filetype)
        VALUES (?, ?, ?)
        """,
        (
            page_item.get('filename', None),
            page_item.get('title', ''),
            page_item.get('filetype', None)
        )
    )
    conn.commit()
    conn.close()

def write_page_images_to_db(page_id, image_filenames):
    """
    Writes image filenames to the 'page_images' table in the SQLite database at 'db/sqlite.db'.

    Args:
        page_id (int): The ID of the page to associate images with.
        image_filenames (list): List of image filenames to write.
    """
    pass  # TODO: Implement page images writing logic

def read_page_images_from_db(page_id):
    """
    Reads image filenames for a given page from the 'page_images' table in the SQLite database at 'db/sqlite.db'.

    Args:
        page_id (int): The ID of the page to read images for.

    Returns:
        list: List of image filenames associated with the page.
    """
    pass  # TODO: Implement page images reading logic

def write_page_image_item_to_db(page_id, filename):
    """
    Writes a single image filename to the 'page_images' table in the SQLite database at 'db/sqlite.db'.

    Args:
        page_id (int): The ID of the page to associate the image with.
        filename (str): The image filename to write.
    """
    pass  # TODO: Implement single page image item writing logic

def read_page_image_item_from_db(image_id):
    """
    Reads a single image item from the 'page_images' table in the SQLite database at 'db/sqlite.db'.

    Args:
        image_id (int): The ID of the image item to read.

    Returns:
        dict: The image item data.
    """
    pass  # TODO: Implement single page image item reading logic

def print_table(table_name):
    """
    Prints all rows from the specified table in the SQLite database at 'db/sqlite.db' in a readable table format.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    # Get column names
    col_names = [description[0] for description in cursor.description]
    # Print header
    print(" | ".join(col_names))
    print("-" * (len(col_names) * 15))
    # Print rows
    for row in rows:
        print(" | ".join(str(item) if item is not None else "" for item in row))
    conn.close()

