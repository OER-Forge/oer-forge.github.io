"""
Module: scan

Purpose: Scans _config.yml and content/ for site information, table of contents information, and page information. Writes SQLite database with three tables: site, toc, and page.
"""

import os
import sqlite3

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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            title TEXT,
            filetype TEXT,
            "order" INTEGER
        )
    """)

    # Create page table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS page (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            title TEXT,
            filetype TEXT,
            convert_md BOOLEAN,
            convert_ipynb BOOLEAN,
            convert_docx BOOLEAN,
            convert_tex BOOLEAN,
            convert_pdf BOOLEAN,
            convert_jupyter BOOLEAN,
            built_ok_md BOOLEAN,
            built_ok_ipynb BOOLEAN,
            built_ok_docx BOOLEAN,
            built_ok_tex BOOLEAN,
            built_ok_pdf BOOLEAN,
            built_ok_jupyter BOOLEAN,
            wcag_ok_md BOOLEAN,
            wcag_ok_ipynb BOOLEAN,
            wcag_ok_docx BOOLEAN,
            wcag_ok_tex BOOLEAN,
            wcag_ok_pdf BOOLEAN,
            wcag_ok_jupyter BOOLEAN,
            filename_md TEXT,
            filename_ipynb TEXT,
            filename_docx TEXT,
            filename_tex TEXT,
            filename_pdf TEXT,
            filename_jupyter TEXT,  
            toc_id INTEGER
        )
    """)
    
    # Create page_images table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS page_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id INTEGER,
            filename TEXT,
            FOREIGN KEY(page_id) REFERENCES page(id)
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
    import yaml
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
    """
    Reads table of contents information from the '_config.yml' file and writes it to the 'toc' table in the SQLite database at 'db/sqlite.db'.
    """
    import yaml
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_root, '_config.yml')
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    toc_items = config.get('toc', [])

    def insert_toc_items(items, order=0):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for idx, item in enumerate(items):
            title = item.get('title', '')
            filename = item.get('file', '')
            filetype = os.path.splitext(filename)[1][1:] if filename else ''
            cursor.execute(
                """
                INSERT INTO toc (filename, title, filetype, "order")
                VALUES (?, ?, ?, ?)
                """,
                (filename, title, filetype, order + idx)
            )
            toc_id = cursor.lastrowid
            # Recursively insert children
            if 'children' in item:
                insert_toc_items(item['children'], order=0)
        conn.commit()
        conn.close()

    insert_toc_items(toc_items)

def read_toc_item_from_db(item_id):
    """
    Reads a single TOC item from the 'toc' table in the SQLite database at 'db/sqlite.db'.

    Args:
        item_id (int): The ID of the TOC item to read.

    Returns:
        dict: The TOC item data.
    """
    pass  # TODO: Implement TOC item reading logic


def write_toc_item_to_db(toc_item):
    """
    Writes a single TOC item to the 'toc' table in the SQLite database at 'db/sqlite.db'.

    Args:
        toc_item (dict): The TOC item data to write.
    """
    pass  # TODO: Implement TOC item writing logic


def read_page_info_from_config():
    """
    Reads page information from the '_config.yml' file in the project root.

    Returns:
        list: Page information parsed from the YAML configuration file.
    """
    pass  # TODO: Implement page info reading logic


def write_page_info_to_db(page_info):
    """
    Writes page information to the 'page' table in the SQLite database at 'db/sqlite.db'.

    Args:
        page_info (list): List of page information to write to the database.
    """
    pass  # TODO: Implement page info writing logic


def read_page_item_from_db(page_id):
    """
    Reads a single page item from the 'page' table in the SQLite database at 'db/sqlite.db'.

    Args:
        page_id (int): The ID of the page item to read.

    Returns:
        dict: The page item data.
    """
    pass  # TODO: Implement page item reading logic


def write_page_item_to_db(page_item):
    """
    Writes a single page item to the 'page' table in the SQLite database at 'db/sqlite.db'.

    Args:
        page_item (dict): The page item data to write.
    """
    pass  # TODO: Implement page item writing logic

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

