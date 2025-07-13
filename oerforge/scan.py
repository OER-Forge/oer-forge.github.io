"""
Module: scan

Purpose: Scans _config.yml and content/ for site information, table of contents information, and page information. Writes SQLite database with three tables: site, toc, and page.
"""
import os
import sqlite3
import yaml
import nbformat
from markdown_it import MarkdownIt

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
    cursor.execute("DROP TABLE IF EXISTS build_images")
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
            page_filepath TEXT,
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
            page_level INTEGER,  
            page_toc_id INTEGER,
            FOREIGN KEY(page_toc_id) REFERENCES toc(toc_id)
        )
    """)
    
    # Create page_images table
    # In initialize_database()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS page_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_page_id INTEGER,
            image_filename TEXT,
            image_remote BOOLEAN,
            image_type TEXT,
            image_filepath TEXT,
            image_url TEXT,
            image_downloaded BOOLEAN,
            image_relocated_filename TEXT,
            image_generated BOOLEAN DEFAULT 0,
            image_generated_cell_index INTEGER,
            image_generated_output_index INTEGER,
            image_generated_caption TEXT,
            FOREIGN KEY(image_page_id) REFERENCES page(page_id)
        )
    """)
    
    # Create build_images table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS build_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT,
            image_rel_path TEXT,
            image_ext TEXT,
            image_size INTEGER,
            image_found BOOLEAN
        )
    """)

    conn.commit()
    conn.close()

# --- New Files Table and Linking ---
def create_files_table():
    """
    Creates the 'files' and 'pages_files' tables in the SQLite database for tracking all linked files (images, PDFs, docs, remote files) and their references.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS files")
    cursor.execute("DROP TABLE IF EXISTS pages_files")
    # Create files table
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
    # Create pages_files table (many-to-many)
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
    """
    Parses a markdown file and extracts all linked files (images, PDFs, docs, remote files), ignoring HTML and YouTube links.
    Returns a list of file records to be inserted into the files table.
    Uses markdown-it-py for robust parsing.
    """
    import mimetypes
    from markdown_it import MarkdownIt
    import os
    file_records = []
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        md = MarkdownIt()
        tokens = md.parse(md_text)
        for token in tokens:
            # Inline tokens may contain children (images, links)
            if token.type == "inline" and token.children:
                for child in token.children:
                    # Images
                    if child.type == "image":
                        src = child.attrs.get("src") if child.attrs else None
                        if src:
                            ext = os.path.splitext(src)[1][1:].lower()
                            mime_type, _ = mimetypes.guess_type(src)
                            is_image = mime_type and mime_type.startswith("image/")
                            is_remote = src.startswith("http://") or src.startswith("https://")
                            file_records.append({
                                "filename": os.path.basename(src),
                                "extension": ext,
                                "mime_type": mime_type or "",
                                "is_image": int(is_image),
                                "is_remote": int(is_remote),
                                "url": src if is_remote else "",
                                "referenced_page": md_path,
                                "relative_path": src,
                                "absolute_path": os.path.abspath(src) if not is_remote else ""
                            })
                    # Links (non-image)
                    elif child.type == "link":
                        href = child.attrs.get("href") if child.attrs else None
                        if href:
                            ext = os.path.splitext(href)[1][1:].lower()
                            mime_type, _ = mimetypes.guess_type(href)
                            is_image = mime_type and mime_type.startswith("image/")
                            is_remote = href.startswith("http://") or href.startswith("https://")
                            # Ignore YouTube and HTML links
                            if "youtube.com" in href or href.endswith(".html"):
                                continue
                            file_records.append({
                                "filename": os.path.basename(href),
                                "extension": ext,
                                "mime_type": mime_type or "",
                                "is_image": int(is_image),
                                "is_remote": int(is_remote),
                                "url": href if is_remote else "",
                                "referenced_page": md_path,
                                "relative_path": href,
                                "absolute_path": os.path.abspath(href) if not is_remote else ""
                            })
        return file_records
    except Exception as e:
        print(f"[ERROR] Failed to extract linked files from {md_path}: {e}")
        return []
            file_record['is_image'],
            file_record['is_remote'],
            file_record['url'],
            file_record['referenced_page'],
            file_record['relative_path'],
            file_record['absolute_path']
        )
    )
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def link_file_to_page(file_id, page_id):
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
    conn.close()
# --- New: Populate files and pages_files from markdown ---
def populate_files_from_markdown():
    """
    Scans all markdown files listed in the 'page' table and populates the files and pages_files tables.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT page_id, page_filepath, page_filename, page_filetype FROM page WHERE page_filetype = 'md'")
    pages = cursor.fetchall()
    conn.close()
    for page_id, filepath, filename, filetype in pages:
        if not filename or not filetype:
            continue
        full_path = os.path.join(filepath, filename) if filepath else filename
        file_records = extract_linked_files_from_markdown(full_path, page_id)
        for file_record in file_records:
            file_id = insert_file_record(file_record)
            link_file_to_page(file_id, page_id)


# --- Build Images Scanning ---
def populate_build_images():
    """
    Scans build/files/assets recursively for all image files and populates the build_images table.
    Columns: image_filename, image_rel_path, image_abs_path, image_ext, image_size, image_found
    """
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(project_root, 'build', 'files', 'assets')
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Clear table first
    cursor.execute("DELETE FROM build_images")
    build_dir = os.path.join(project_root, 'build')
    for dirpath, dirnames, filenames in os.walk(assets_dir):
        for filename in filenames:
            if filename.startswith('.'):
                continue
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, build_dir)
            ext = os.path.splitext(filename)[1][1:].lower()
            try:
                size = os.path.getsize(abs_path)
                found = 1
            except Exception:
                size = 0
                found = 0
            cursor.execute(
                """
                INSERT INTO build_images (image_filename, image_rel_path, image_ext, image_size, image_found)
                VALUES (?, ?, ?, ?, ?)
    """
    Inserts a record into the 'pages_files' table to link a file to a referencing page (many-to-many).
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # page_id here is the path to the page (for markdown, use md_path)
    cursor.execute(
        """
        INSERT INTO pages_files (file_id, page_path)
        VALUES (?, ?)
        """,
        (file_id, page_id)
    )
    conn.commit()
    conn.close()
def scan_and_populate_files_db(md_dir):
    """
    Scans all markdown files in md_dir, extracts linked files, and populates files and pages_files tables.
    """
    import os
    for dirpath, dirnames, filenames in os.walk(md_dir):
        for filename in filenames:
            if filename.startswith('.') or not filename.lower().endswith('.md'):
                continue
            md_path = os.path.join(dirpath, filename)
            # Use md_path as page_id for linking
            file_records = extract_linked_files_from_markdown(md_path, md_path)
            for file_record in file_records:
                file_id = insert_file_record(file_record)
                link_file_to_page(file_id, md_path)
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
                full_path = item['file']
                title = item.get('title', '')
                filetype = os.path.splitext(full_path)[1][1:] if full_path else ''
                filepath, filename = os.path.split(full_path)
                # Set convert flags based on filetype
                convert_map = {
                    "ipynb": dict(md=1, ipynb=1, docx=1, tex=1, pdf=1, jupyter=1),
                    "md": dict(md=1, docx=1, jupyter=1, tex=1, pdf=1),
                    "docx": dict(md=1, docx=1, tex=1, pdf=1),
                    "ppt": dict(pdf=1)
                }
                flags = convert_map.get(filetype, {})
                convert_md = flags.get("md", 0)
                convert_ipynb = flags.get("ipynb", 0)
                convert_docx = flags.get("docx", 0)
                convert_tex = flags.get("tex", 0)
                convert_pdf = flags.get("pdf", 0)
                convert_jupyter = flags.get("jupyter", 0)
                page = {
                    "filepath": filepath,
                    "filename": filename,
                    "title": title,
                    "filetype": filetype,
                    "convert_md": convert_md,
                    "convert_ipynb": convert_ipynb,
                    "convert_docx": convert_docx,
                    "convert_tex": convert_tex,
                    "convert_pdf": convert_pdf,
                    "convert_jupyter": convert_jupyter,
                }
                pages.append(page)
            if 'children' in item:
                pages.extend(collect_pages(item['children']))
        return pages

    page_entries = collect_pages(toc_items)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for page in page_entries:
        cursor.execute("SELECT toc_id FROM toc WHERE toc_filename = ?", (os.path.join(page['filepath'], page['filename']),))
        toc_row = cursor.fetchone()
        page_toc_id = toc_row[0] if toc_row else None

        cursor.execute(
            """
            INSERT INTO page (
                page_filepath, page_filename, page_title, page_filetype,
                page_convert_md, page_convert_ipynb, page_convert_docx,
                page_convert_tex, page_convert_pdf, page_convert_jupyter,
                page_toc_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                page['filepath'], page['filename'], page['title'], page['filetype'],
                page['convert_md'], page['convert_ipynb'], page['convert_docx'],
                page['convert_tex'], page['convert_pdf'], page['convert_jupyter'],
                page_toc_id
            )
        )
    conn.commit()
    conn.close()

def scan_all_images():
    """
    Scans all files listed in the 'page' table and extracts image references, writing them to the page_images table.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT page_id, page_filepath, page_filename, page_filetype FROM page")
    pages = cursor.fetchall()
    conn.close()

    for page_id, filepath, filename, filetype in pages:
        if not filename or not filetype:
            continue
        full_path = os.path.join(filepath, filename) if filepath else filename
        if filetype == "ipynb":
            extract_image_info_from_ipynb(full_path, page_id)
        # elif filetype == "md":
        #     extract_image_info_from_md(full_path, page_id)  

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

def extract_image_info_from_ipynb(ipynb_path, page_id):
    """
    Extracts image references from a Jupyter notebook (.ipynb) file and writes them to the page_images table.
    Handles both markdown-referenced and code-generated images.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_ipynb_path = os.path.join(project_root, ipynb_path)
    image_records = []
    try:
        with open(full_ipynb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        md = MarkdownIt()
        for idx, cell in enumerate(nb.cells):
            if cell.cell_type == "markdown":
                tokens = md.parse(cell.source)
                for token in tokens:
                    if token.type == "inline":
                        for child in token.children or []:
                            if child.type == "image":
                                src = child.attrs.get("src") if child.attrs else None
                                if src:
                                    ext = os.path.splitext(src)[1].lower().replace('.', '')
                                    is_remote = 1 if src.startswith('http://') or src.startswith('https://') else 0
                                    filepath, filename = os.path.split(src)
                                    image_records.append({
                                        'image_filename': filename,
                                        'image_remote': is_remote,
                                        'image_type': ext,
                                        'image_filepath': filepath,
                                        'image_url': src if is_remote else '',
                                        'image_downloaded': 0,
                                        'image_relocated_filename': '',
                                        'image_generated': 0,
                                        'image_generated_cell_index': None,
                                        'image_generated_output_index': None,
                                        'image_generated_caption': None
                                    })
            elif cell.cell_type == "code":
                # Check for code-generated images in outputs
                for out_idx, output in enumerate(cell.get('outputs', [])):
                    if output.get('data'):
                        for mime, data in output['data'].items():
                            if mime.startswith('image/'):
                                ext = mime.split('/')[-1]
                                # If nbconvert or your pipeline provides a filename, use it
                                filename = output.get('metadata', {}).get('filenames', {}).get(mime, '')
                                relocated_filename = filename if filename else f"codeimg_{page_id}_{idx}_{out_idx}.{ext}"
                                image_records.append({
                                    'image_filename': relocated_filename,
                                    'image_remote': 0,
                                    'image_type': ext,
                                    'image_filepath': '',
                                    'image_url': '',
                                    'image_downloaded': 1,
                                    'image_relocated_filename': relocated_filename,
                                    'image_generated': 1,
                                    'image_generated_cell_index': idx,
                                    'image_generated_output_index': out_idx,
                                    'image_generated_caption': output.get('metadata', {}).get('caption', None)
                                })
        if image_records:
            write_page_images_to_db(page_id, image_records)
    except Exception as e:
        print(f"[ERROR] Failed to extract images from {ipynb_path}: {e}")



def write_page_images_to_db(page_id, image_records):
    """
    Writes image records to the page_images table.
    image_records: list of dicts with keys:
        - image_filename
        - image_remote
        - image_type
        - image_filepath
        - image_url
        - image_downloaded
        - image_relocated_filename
        - image_generated
        - image_generated_cell_index
        - image_generated_output_index
        - image_generated_caption
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for img in image_records:
        cursor.execute(
            """INSERT INTO page_images (
                image_page_id, image_filename, image_remote, image_type, image_filepath, image_url,
                image_downloaded, image_relocated_filename, image_generated, image_generated_cell_index,
                image_generated_output_index, image_generated_caption
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                page_id,
                img.get('image_filename', ''),
                img.get('image_remote', 0),
                img.get('image_type', ''),
                img.get('image_filepath', ''),
                img.get('image_url', ''),
                img.get('image_downloaded', 0),
                img.get('image_relocated_filename', ''),
                img.get('image_generated', 0),
                img.get('image_generated_cell_index', None),
                img.get('image_generated_output_index', None),
                img.get('image_generated_caption', None)
            )
        )
    conn.commit()
    conn.close()

def read_page_images_from_db(page_id):
    """
    Reads image records for a given page from the 'page_images' table in the SQLite database.
    Returns a list of dicts with all image info.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM page_images WHERE image_page_id = ?", (page_id,))
    rows = cursor.fetchall()
    col_names = [description[0] for description in cursor.description]
    conn.close()
    return [dict(zip(col_names, row)) for row in rows]


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
    
def verify_toc_page_link():
    """
    Verifies that each page's page_toc_id points to a TOC entry with a matching filename.
    Prints [OK] if linked correctly, [ERROR] otherwise.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT page.page_id, page.page_filename, page.page_toc_id, toc.toc_filename
        FROM page
        LEFT JOIN toc ON page.page_toc_id = toc.toc_id
    """)
    for row in cursor.fetchall():
        page_id, page_filename, page_toc_id, toc_filename = row
        if page_toc_id is None:
            print(f"[ERROR] Page ID {page_id} ('{page_filename}') is not linked to any TOC entry.")
        elif page_filename == toc_filename:
            print(f"[OK] Page ID {page_id} ('{page_filename}') correctly linked to TOC entry.")
        else:
            print(f"[ERROR] Page ID {page_id} ('{page_filename}') linked to TOC entry with mismatched filename ('{toc_filename}').")
    conn.close()