"""
scan.py: Asset database logic for pages and files only.
"""
import os
import sqlite3

def initialize_database():
    """
    Initializes the SQLite database with 'files' and 'pages_files' tables for asset tracking.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(project_root, 'db')
    db_path = os.path.join(db_dir, 'sqlite.db')
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS files")
    cursor.execute("DROP TABLE IF EXISTS pages_files")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            extension TEXT,
            mime_type TEXT,
            is_image BOOLEAN,
            is_remote BOOLEAN,
            url TEXT,
            referenced_page TEXT,
            relative_path TEXT,
            absolute_path TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            page_path TEXT,
            FOREIGN KEY(file_id) REFERENCES files(id)
        )
    """)
    conn.commit()
    conn.close()

def extract_linked_files_from_markdown(md_path, page_id):
    """
    Parses a markdown file and extracts all linked files (images, PDFs, docs, remote files), ignoring HTML and YouTube links.
    Returns a list of file records to be inserted into the files table.
    """
    import re
    from mimetypes import guess_type
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_md_path = os.path.join(project_root, md_path)
    file_records = []
    try:
        with open(full_md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        # Find all markdown image links ![alt](src)
        img_links = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md_text)
        # Find all markdown file links [text](src)
        file_links = re.findall(r'(?<!\!)\[[^\]]*\]\(([^)]+)\)', md_text)
        all_links = set(img_links + file_links)
        for src in all_links:
            ext = os.path.splitext(src)[1][1:].lower()
            mime_type, _ = guess_type(src)
            is_image = 1 if mime_type and mime_type.startswith('image/') else 0
            is_remote = 1 if src.startswith('http://') or src.startswith('https://') else 0
            filename = os.path.basename(src)
            file_record = {
                'filename': filename,
                'extension': ext,
                'mime_type': mime_type or '',
                'is_image': is_image,
                'is_remote': is_remote,
                'url': src if is_remote else '',
                'referenced_page': md_path,
                'relative_path': src if not is_remote else '',
                'absolute_path': os.path.abspath(os.path.join(os.path.dirname(full_md_path), src)) if not is_remote else ''
            }
            file_records.append(file_record)
    except Exception as e:
        print(f"[ERROR] Failed to extract linked files from {md_path}: {e}")
    return file_records

def insert_file_record(file_record):
    """
    Inserts a single file record into the 'files' table.
    Returns the inserted file_id.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO files (filename, extension, mime_type, is_image, is_remote, url, referenced_page, relative_path, absolute_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            file_record.get('filename', ''),
            file_record.get('extension', ''),
            file_record.get('mime_type', ''),
            file_record.get('is_image', 0),
            file_record.get('is_remote', 0),
            file_record.get('url', ''),
            file_record.get('referenced_page', ''),
            file_record.get('relative_path', ''),
            file_record.get('absolute_path', '')
        )
    )
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def link_file_to_page(file_id, page_path):
    """
    Inserts a record into the 'pages_files' table to link a file to a referencing page (many-to-many).
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO pages_files (file_id, page_path)
        VALUES (?, ?)
        """,
        (file_id, page_path)
    )
    conn.commit()
    conn.close()

def scan_and_populate_files_db(md_dir):
    """
    Scans all markdown files in md_dir, extracts linked files, and populates files and pages_files tables.
    """
    for dirpath, dirnames, filenames in os.walk(md_dir):
        for filename in filenames:
            if filename.startswith('.') or not filename.lower().endswith('.md'):
                continue
            md_path = os.path.join(dirpath, filename)
            file_records = extract_linked_files_from_markdown(md_path, md_path)
            for file_record in file_records:
                file_id = insert_file_record(file_record)
                link_file_to_page(file_id, md_path)

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
    col_names = [description[0] for description in cursor.description]
    print(" | ".join(col_names))
    print("-" * (len(col_names) * 15))
    for row in rows:
        print(" | ".join(str(item) if item is not None else "" for item in row))
    conn.close()

__all__ = [
    "initialize_database",
    "extract_linked_files_from_markdown",
    "insert_file_record",
    "link_file_to_page",
    "scan_and_populate_files_db",
    "print_table"
]
