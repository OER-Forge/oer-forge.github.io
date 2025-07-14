import sqlite3
import os

# ------------------------------------------------------------------------------
# Database Initialization and Utility Functions for OERForge Asset Tracking
# ------------------------------------------------------------------------------

def initialize_database():
    """
    Initializes the SQLite database for asset tracking in the OERForge project.

    This function creates the following tables:
        - files: Stores metadata about tracked files/assets.
        - pages_files: Maps files to pages where they are referenced.
        - pages: Tracks source and output paths for pages.
        - site_info: Stores site-wide metadata and configuration.

    Existing tables are dropped before creation to ensure a clean state.
    The database file is located at <project_root>/db/sqlite.db.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(project_root, 'db')
    db_path = os.path.join(db_dir, 'sqlite.db')
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS files")
    cursor.execute("DROP TABLE IF EXISTS pages_files")
    cursor.execute("DROP TABLE IF EXISTS content")
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
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_path TEXT,
            output_path TEXT,
            is_autobuilt BOOLEAN DEFAULT 0,
            mime_type TEXT,
            can_convert_md BOOLEAN DEFAULT NULL,
            can_convert_tex BOOLEAN DEFAULT NULL,
            can_convert_pdf BOOLEAN DEFAULT NULL,
            can_convert_docx BOOLEAN DEFAULT NULL,
            can_convert_ppt BOOLEAN DEFAULT NULL,
            can_convert_jupyter BOOLEAN DEFAULT NULL,
            can_convert_ipynb BOOLEAN DEFAULT NULL,
            converted_md BOOLEAN DEFAULT NULL,
            converted_tex BOOLEAN DEFAULT NULL,
            converted_pdf BOOLEAN DEFAULT NULL,
            converted_docx BOOLEAN DEFAULT NULL,
            converted_ppt BOOLEAN DEFAULT NULL,
            converted_jupyter BOOLEAN DEFAULT NULL,
            converted_ipynb BOOLEAN DEFAULT NULL,
            wcag_status_html TEXT DEFAULT NULL
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

def log_event(message, level="INFO"):
    """
    Logs an event to both stdout and a log file in the project root.

    Args:
        message (str): The log message to record.
        level (str): The severity level (e.g., "INFO", "ERROR", "WARNING").

    The log file is named 'scan.log' and is located at <project_root>/scan.log.
    Each log entry is timestamped.
    """
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] [{level}] {message}\n"
    print(log_line, end="")
    # Write to db.log in project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(project_root, 'db.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_line)
    except Exception as e:
        print(f"[ERROR] Could not write to log file: {e}")

def get_db_connection(db_path=None):
    """
    Returns a sqlite3 connection to the database.

    Args:
        db_path (str, optional): Path to the SQLite database file.
            If None, defaults to <project_root>/db/sqlite.db.

        sqlite3.Connection: A connection object to the SQLite database.
    """
    if db_path is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, 'db', 'sqlite.db')
    return sqlite3.connect(db_path)

def insert_file_records(file_records, db_path=None):
    """
    Batch inserts multiple file records into the 'files' table.

    Args:
        file_records (list of dict): Each dict contains file metadata fields.
        db_path (str, optional): Path to the SQLite database file.

        list of int: List of inserted file_ids (primary keys).

    Example file_record dict keys:
        - filename, extension, mime_type, is_image, is_remote, url,
          referenced_page, relative_path, absolute_path, cell_type,
          is_code_generated, is_embedded
    """
def insert_file_records(file_records, db_path=None, conn=None, cursor=None):
    import threading
    import time
    close_conn = False
    if conn is None or cursor is None:
        conn = get_db_connection(db_path)
        log_event(f"[DEBUG][{os.getpid()}][{threading.get_ident()}] Opened DB connection in insert_file_records at {time.time()}", level="DEBUG")
        cursor = conn.cursor()
        close_conn = True
    file_ids = []
    for file_record in file_records:
        cursor.execute(
            """
            INSERT INTO files (filename, extension, mime_type, is_image, is_remote, url, referenced_page, relative_path, absolute_path, cell_type, is_code_generated, is_embedded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                file_record.get('absolute_path', ''),
                file_record.get('cell_type', None),
                file_record.get('is_code_generated', None),
                file_record.get('is_embedded', None)
            )
        )
        file_ids.append(cursor.lastrowid)
    log_event(f"[DEBUG][{os.getpid()}][{threading.get_ident()}] Committing DB in insert_file_records at {time.time()}", level="DEBUG")
    try:
        conn.commit()
    except Exception as e:
        import traceback
        log_event(f"[ERROR][{os.getpid()}][{threading.get_ident()}] Commit failed in insert_file_records: {e}\n{traceback.format_exc()}", level="ERROR")
        raise
    if close_conn:
        log_event(f"[DEBUG][{os.getpid()}][{threading.get_ident()}] Closing DB connection in insert_file_records at {time.time()}", level="DEBUG")
        conn.close()
    return file_ids

def link_files_to_pages(file_page_pairs, db_path=None):
    """
    Batch inserts records into the 'pages_files' table to link files to pages.

    Args:
        file_page_pairs (list of tuple): Each tuple is (file_id, page_path).
        db_path (str, optional): Path to the SQLite database file.

    This function creates associations between files and the pages where they are referenced.
    """
def link_files_to_pages(file_page_pairs, db_path=None, conn=None, cursor=None):
    import threading
    import time
    close_conn = False
    if conn is None or cursor is None:
        conn = get_db_connection(db_path)
        log_event(f"[DEBUG][{os.getpid()}][{threading.get_ident()}] Opened DB connection in link_files_to_pages at {time.time()}", level="DEBUG")
        cursor = conn.cursor()
        close_conn = True
    for file_id, page_path in file_page_pairs:
        cursor.execute(
            """
            INSERT INTO pages_files (file_id, page_path)
            VALUES (?, ?)
            """,
            (file_id, page_path)
        )
    log_event(f"[DEBUG][{os.getpid()}][{threading.get_ident()}] Committing DB in link_files_to_pages at {time.time()}", level="DEBUG")
    try:
        conn.commit()
    except Exception as e:
        import traceback
        log_event(f"[ERROR][{os.getpid()}][{threading.get_ident()}] Commit failed in link_files_to_pages: {e}\n{traceback.format_exc()}", level="ERROR")
        raise
    if close_conn:
        log_event(f"[DEBUG][{os.getpid()}][{threading.get_ident()}] Closing DB connection in link_files_to_pages at {time.time()}", level="DEBUG")
        conn.close()

def pretty_print_table(table_name, db_path=None):
    """
    Prints a database table in a readable, aligned format with column headers.

    Args:
        table_name (str): Name of the table to print.
        db_path (str, optional): Path to the SQLite database file.

    This function is useful for debugging and inspecting table contents.
    """
    if db_path is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, 'db', 'sqlite.db')
def pretty_print_table(table_name, db_path=None, conn=None, cursor=None):
    import threading
    import time
    close_conn = False
    if conn is None or cursor is None:
        conn = sqlite3.connect(db_path)
        log_event(f"[DEBUG][{os.getpid()}][{threading.get_ident()}] Opened DB connection in pretty_print_table at {time.time()}", level="DEBUG")
        cursor = conn.cursor()
        close_conn = True
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    col_names = [description[0] for description in cursor.description]
    # Calculate column widths for pretty printing
    col_widths = [max(len(str(col)), max((len(str(row[i])) for row in rows), default=0)) for i, col in enumerate(col_names)]
    # Print header row
    header = " | ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(col_names))
    log_event(header, level="INFO")
    log_event("-" * len(header), level="INFO")
    # Print each row
    for row in rows:
        log_event(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))), level="INFO")
    if close_conn:
        log_event(f"[DEBUG][{os.getpid()}][{threading.get_ident()}] Closing DB connection in pretty_print_table at {time.time()}", level="DEBUG")
        conn.close()

