"""
scan.py: Asset database logic for pages and files only.
"""
import os
import sqlite3

def batch_read_files(file_paths):
    """
    Reads multiple files and returns their contents as a dict: {path: content}
    Supports markdown (.md), notebook (.ipynb), docx (.docx), and other file types.
    """
    contents = {}
    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == '.md':
                contents[path] = read_markdown_file(path)
            elif ext == '.ipynb':
                contents[path] = read_notebook_file(path)
            elif ext == '.docx':
                contents[path] = read_docx_file(path)
            else:
                contents[path] = None
        except Exception as e:
            print(f"[ERROR] Could not read {path}: {e}")
            contents[path] = None
    return contents

def read_markdown_file(path):
    """
    Reads a markdown (.md) file and returns its content as a string.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] Could not read markdown file {path}: {e}")
        return None

def read_notebook_file(path):
    """
    Reads a Jupyter notebook (.ipynb) file and returns its content as a dict.
    """
    import json
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not read notebook file {path}: {e}")
        return None

def read_docx_file(path):
    """
    Reads a docx file and returns its text content as a string.
    Requires python-docx to be installed.
    """
    try:
        from docx import Document
        doc = Document(path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '\n'.join(text)
    except ImportError:
        print("[ERROR] python-docx is not installed. Run 'pip install python-docx' in your environment.")
        return None
    except Exception as e:
        print(f"[ERROR] Could not read docx file {path}: {e}")
        return None

def batch_extract_assets(contents_dict, content_type, **kwargs):
    """
    Extracts assets from multiple file contents in one pass.
    contents_dict: {path: content}
    content_type: 'markdown', 'notebook', 'docx', etc.
    Returns a dict: {path: [asset_records]}
    """
    assets = {}
    # TODO: Implement batch asset extraction logic for each content type
    return assets

def extract_linked_files_from_markdown_content(md_text, page_id=None):
    """
    Extracts asset links from markdown text.
    Returns a list of file records.
    """
    # TODO: Implement markdown asset extraction logic
    return []

def extract_linked_files_from_notebook_cell_content(cell, nb_path=None):
    """
    Extracts asset links from a notebook cell.
    Returns a list of file records.
    """
    # TODO: Implement notebook cell asset extraction logic
    return []

def extract_linked_files_from_docx_content(docx_path, page_id=None):
    """
    Extracts asset links from a docx file.
    Returns a list of file records.
    """
    # TODO: Implement docx asset extraction logic
    return []

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

def parse_toc_and_populate_pages(config_path):
    """
    Parses the toc: from _config.yml and populates the pages table with hierarchy, menu, autogen, parent, order, and depth info.
    Logs missing and duplicate files.
    """
    import yaml
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'db', 'sqlite.db')
    full_config_path = os.path.join(project_root, config_path)
    with open(full_config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    toc = config.get('toc', [])
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pages")
    seen_paths = set()

    def walk_toc(items, parent_id=None, depth=0):
        for idx, item in enumerate(items):
            title = item.get('title', '')
            file_path = item.get('file')
            is_menu_item = int(item.get('menu', False))
            is_autogen = int(file_path is None)
            was_autogenerated = 0  # Set to 1 if/when actually generated
            order = idx
            # Insert page record
            if file_path:
                source_path = file_path
                output_path = None
                if source_path in seen_paths:
                    log_event(f"TOC: Duplicate file path '{source_path}' in toc", level="WARN")
                seen_paths.add(source_path)
                # Check if file exists
                abs_path = os.path.join(project_root, source_path)
                if not os.path.exists(abs_path):
                    log_event(f"TOC: Missing file '{source_path}' (expected at {abs_path})", level="ERROR")
                cursor.execute(
                    """
                    INSERT INTO pages (title, source_path, output_path, is_autobuilt, is_menu_item, is_autogen, was_autogenerated, parent_id, "order", depth)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (title, source_path, output_path, 0, is_menu_item, is_autogen, was_autogenerated, parent_id, order, depth)
                )
                page_id = cursor.lastrowid
            else:
                # Autogenerated node
                cursor.execute(
                    """
                    INSERT INTO pages (title, source_path, output_path, is_autobuilt, is_menu_item, is_autogen, was_autogenerated, parent_id, "order", depth)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (title, None, None, 0, is_menu_item, is_autogen, was_autogenerated, parent_id, order, depth)
                )
                page_id = cursor.lastrowid
            # Recursively process children
            children = item.get('children', [])
            if children:
                walk_toc(children, parent_id=page_id, depth=depth+1)

    walk_toc(toc, parent_id=None, depth=0)
    conn.commit()
    conn.close()