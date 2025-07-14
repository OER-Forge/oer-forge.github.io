def batch_read_files(file_paths):
    """
    Reads multiple files and returns their contents as a dict: {path: content}
    """
    # TODO: Implement batch file reading logic
    pass

def batch_extract_assets(contents_dict, content_type, **kwargs):
    """
    Extracts assets from multiple file contents.
    contents_dict: {path: content}
    Returns a dict: {path: [asset_records]}
    """
    # TODO: Implement batch asset extraction logic
    pass
def insert_file_records(file_records):
    """
    Batch inserts multiple file records into the 'files' table.
    file_records: list of file record dicts.
    Returns a list of inserted file_ids.
    """
    # TODO: Implement batch insertion logic
    pass
def link_files_to_pages(file_page_pairs):
    """
    Batch inserts records into the 'pages_files' table.
    file_page_pairs: list of (file_id, page_path) tuples.
    """
    # TODO: Implement batch linking logic
    pass
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
    cursor.execute("DROP TABLE IF EXISTS pages")
    cursor.execute("DROP TABLE IF EXISTS site_info")
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
            absolute_path TEXT,
            cell_type TEXT,
            is_code_generated BOOLEAN,
            is_embedded BOOLEAN
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_path TEXT,
            output_path TEXT,
            is_autobuilt BOOLEAN DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS site_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            description TEXT,
            logo TEXT,
            favicon TEXT,
            theme_default TEXT,
            theme_light TEXT,
            theme_dark TEXT,
            language TEXT,
            github_url TEXT,
            footer_text TEXT,
            header TEXT
        );
    """)
    
def populate_site_info_from_config(config_path):
    """
    Reads _config.yml and populates the site_info table with site and footer info.
    """
    import yaml
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    full_config_path = os.path.join(project_root, config_path)
    with open(full_config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    site = config.get('site', {})
    footer = config.get('footer', {})
    theme = site.get('theme', {})
    # Read header.html contents
    header_html_path = os.path.join(project_root, 'static', 'templates', 'header.html')
    try:
        with open(header_html_path, 'r', encoding='utf-8') as hf:
            header_html = hf.read()
    except Exception:
        header_html = ''
    print('[DEBUG] header_html read from file (first 500 chars):', repr(header_html)[:500])
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM site_info")
    cursor.execute(
        """
        INSERT INTO site_info (title, author, description, logo, favicon, theme_default, theme_light, theme_dark, language, github_url, footer_text, header)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            site.get('title', ''),
            site.get('author', ''),
            site.get('description', ''),
            site.get('logo', ''),
            site.get('favicon', ''),
            theme.get('default', ''),
            theme.get('light', ''),
            theme.get('dark', ''),
            site.get('language', ''),
            site.get('github_url', ''),
            footer.get('text', ''),
            header_html
        )
    )
    conn.commit()
    conn.close()


def extract_linked_files_from_content(content, content_type, **kwargs):
    """
    Dispatches asset extraction based on content_type ('markdown', 'notebook_cell', 'docx').
    Returns a list of file records.
    """
    if content_type == 'markdown':
        return extract_linked_files_from_markdown_content(content, **kwargs)
    elif content_type == 'notebook_cell':
        return extract_linked_files_from_notebook_cell_content(content, **kwargs)
    elif content_type == 'docx':
        return extract_linked_files_from_docx_content(content, **kwargs)
    else:
        return []

def extract_linked_files_from_markdown_content(md_text, page_id):
    """
    Extracts asset links from markdown text.
    Returns a list of file records.
    """
    # TODO: Implement markdown asset extraction logic
    pass

def extract_linked_files_from_notebook_cell_content(cell, nb_path):
    """
    Extracts asset links from a notebook cell.
    Returns a list of file records.
    """
    # TODO: Implement notebook cell asset extraction logic
    pass

def extract_linked_files_from_docx_content(docx_path, page_id):
    """
    Extracts asset links from a docx file.
    Returns a list of file records.
    """
    # TODO: Implement docx asset extraction logic
    pass

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
    Orchestrates modular asset scanning for markdown, notebook, and docx files.
    """
    # Example usage: scan_and_populate_files_db(md_dir, toc_path)
    pass

def scan_markdown_files(md_dir, toc_path):
    """
    Scans markdown files listed in toc and populates files and pages_files tables.
    """
    # TODO: Implement markdown scanning logic
    pass

def scan_notebook_files(notebook_paths):
    """
    Scans notebook files and populates files and pages_files tables.
    """
    # TODO: Implement notebook scanning logic
    pass

def scan_docx_files(docx_paths):
    """
    Scans docx files and populates files and pages_files tables.
    """
    # TODO: Implement docx scanning logic
    pass

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

# --- Notebook Asset Scanning Stubs ---
def get_notebook_paths_from_toc(toc_path):
    """
    Parses a toc file (plain text, one file per line) and returns a list of .ipynb notebook paths to scan.
    Only returns notebooks listed in toc.
    Logs found and ignored entries.
    """
    notebook_paths = []
    try:
        with open(toc_path, 'r', encoding='utf-8') as f:
            for line in f:
                entry = line.strip()
                if not entry or entry.startswith('#'):
                    continue
                if entry.lower().endswith('.ipynb'):
                    notebook_paths.append(entry)
                    log_event(f"TOC: Found notebook entry: {entry}", level="INFO")
                else:
                    log_event(f"TOC: Ignored non-notebook entry: {entry}", level="DEBUG")
    except Exception as e:
        log_event(f"Error reading TOC file {toc_path}: {e}", level="ERROR")
    return notebook_paths

def scan_notebook_for_assets(nb_path):
    """
    Scans a notebook for assets (images/files) in all cells.
    Calls extract_images_from_notebook_cell for each cell.
    """
    # TODO: Implement notebook scanning logic
    pass

def extract_images_from_notebook_cell(cell, nb_path):
    """
    Extracts images/files from a single notebook cell.
    Records cell_type, is_code_generated, is_embedded, and logs warnings if expected images are missing.
    Returns a list of file records.
    """
    # TODO: Implement image extraction logic
    return []

def log_event(message, level="INFO"):
    """
    Logs an event to both stdout and a log file in the project root.
    """
    import datetime
    import os
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] [{level}] {message}\n"
    print(log_line, end="")
    # Write to scan.log in project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(project_root, 'scan.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_line)
    except Exception as e:
        print(f"[ERROR] Could not write to log file: {e}")

def insert_notebook_file_record(file_record):
    """
    Inserts a notebook file record into the 'files' table, supporting new fields (cell_type, is_code_generated, is_embedded).
    Returns the inserted file_id.
    """
    # TODO: Extend DB schema and implement insertion logic
    pass

__all__ = [
    "initialize_database",
    "extract_linked_files_from_markdown",
    "insert_file_record",
    "link_file_to_page",
    "scan_and_populate_files_db",
    "print_table"
]
