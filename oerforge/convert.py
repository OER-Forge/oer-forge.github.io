"""
convert.py

Module for converting Jupyter notebooks (.ipynb) and Markdown files to various formats,
managing associated images, and updating a SQLite database with conversion status.

Main features:
- Executes notebooks and exports to Markdown.
- Handles image extraction, copying, and reference updates.
- Logs conversion actions and updates database flags.
- Provides stub functions for other conversions (docx, tex, pdf).

Author: [Your Name]
"""

import sys
import os
import shutil
import sqlite3
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor, ExtractOutputPreprocessor
from traitlets.config import Config

# --- Constants ---
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "sqlite.db")
CONTENT_ROOT = "content"
BUILD_ROOT = "build/files"
LOG_DIR = "log"

# --- Environment and Dependency Checks ---

def check_venv_and_packages():
    """
    Ensure the script is running inside the correct virtual environment and
    required Python packages are installed.
    """
    venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        os.path.abspath(sys.prefix).startswith(os.path.abspath(venv_path))
    )
    print(f"[DEBUG] sys.prefix: {sys.prefix}")
    print(f"[DEBUG] venv_path: {venv_path}")
    print(f"[DEBUG] in_venv: {in_venv}")
    if not in_venv:
        print("[ERROR] You are not running inside the .venv environment.")
        print(f"Activate it with: source {venv_path}/bin/activate")
        sys.exit(1)

    required = ["matplotlib", "numpy", "scipy"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
            print(f"[DEBUG] Package '{pkg}' is available.")
        except ImportError:
            print(f"[DEBUG] Package '{pkg}' is MISSING.")
            missing.append(pkg)
    if missing:
        print(f"[ERROR] Missing required packages: {', '.join(missing)}")
        print(f"Install them with: pip install {' '.join(missing)}")
        sys.exit(1)

check_venv_and_packages()

# --- Database Helpers ---

def get_db_connection(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    """
    print(f"[DEBUG] Connecting to DB at {db_path}")
    return sqlite3.connect(db_path)

def get_page_info(full_path, conn):
    """
    Retrieve page information from the database for a given file path.
    """
    dir_path, filename = os.path.split(full_path)
    print(f"[DEBUG] get_page_info: dir_path={dir_path}, filename={filename}")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM page WHERE page_filepath=? AND page_filename=?",
        (dir_path, filename)
    )
    result = cursor.fetchone()
    print(f"[DEBUG] get_page_info result: {result}")
    return result

def get_images_for_page(page_id, conn):
    """
    Get all images associated with a page from the database.
    """
    print(f"[DEBUG] get_images_for_page: page_id={page_id}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM page_images WHERE image_page_id=?", (page_id,))
    images = cursor.fetchall()
    print(f"[DEBUG] Found {len(images)} images for page_id {page_id}")
    return images

def update_image_relocated_filename(img_id, new_path, conn):
    """
    Update the relocated filename for an image in the database.
    """
    print(f"[DEBUG] Updating image relocated filename for img_id={img_id} to {new_path}")
    cursor = conn.cursor()
    cursor.execute("UPDATE page_images SET image_relocated_filename=? WHERE id=?", (new_path, img_id))
    conn.commit()

def update_page_conversion_flag(page_id, flag, conn):
    """
    Set a conversion flag (e.g., page_built_ok_md) for a page in the database.
    """
    print(f"[DEBUG] Updating page conversion flag '{flag}' for page_id={page_id}")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE page SET {flag}=1 WHERE page_id=?", (page_id,))
    conn.commit()
    cursor.execute(f"SELECT {flag} FROM page WHERE page_id=?", (page_id,))
    print(f"[DEBUG] {flag} for page_id {page_id} is now:", cursor.fetchone())

# --- File and Directory Utilities ---

def ensure_dir(path):
    """
    Ensure that a directory exists; create it if necessary.
    """
    print(f"[DEBUG] Ensuring directory exists: {path}")
    os.makedirs(path, exist_ok=True)

def copy_file(src, dest):
    """
    Copy a file from src to dest, creating destination directories as needed.
    """
    print(f"[DEBUG] Copying file from {src} to {dest}")
    ensure_dir(os.path.dirname(dest))
    shutil.copy2(src, dest)

def get_build_dir_for_file(src_path):
    """
    Get the build directory for a given source file path.
    """
    rel_dir = os.path.relpath(os.path.dirname(src_path), CONTENT_ROOT)
    build_dir = os.path.join(BUILD_ROOT, rel_dir)
    print(f"[DEBUG] Build dir for {src_path}: {build_dir}")
    ensure_dir(build_dir)
    return build_dir

def log_action(message):
    """
    Append a log message to the conversion log file.
    """
    ensure_dir(LOG_DIR)
    log_path = os.path.join(LOG_DIR, "convert.log")
    print(f"[DEBUG] Logging action: {message}")
    with open(log_path, "a") as logf:
        logf.write(message + "\n")

# --- Image Handling ---

def build_image_map(page_id, conn):
    """
    Build a mapping from original image references to relocated filenames
    for both markdown/static and code-generated images.
    """
    images = get_images_for_page(page_id, conn)
    image_map = {}
    for img in images:
        img_filename = img[2]  # image_filename
        img_remote = img[3]    # image_remote
        img_filepath = img[5]  # image_filepath
        img_url = img[6]       # image_url
        img_relocated_filename = img[8]  # image_relocated_filename
        img_generated = bool(img[9])     # image_generated

        # For code-generated images, use relocated filename as key and value
        if img_generated:
            image_map[img_filename] = img_relocated_filename
        # For remote images, use URL as key
        elif img_remote:
            image_map[img_url] = "REMOTE IMAGE"
        # For static/markdown images, use filepath or filename as key
        else:
            key = img_filepath if img_filepath else img_filename
            image_map[key] = img_relocated_filename if img_relocated_filename else img_filename
    return image_map

def copy_images_for_ipynb(ipynb_path, conn=None):
    """
    Copy all images associated with a notebook to the build directory,
    updating the database and returning an image map.
    Uses relocated filenames for code-generated images.
    """
    print(f"[DEBUG] Copying images for notebook: {ipynb_path}")
    if conn is None:
        conn = get_db_connection()
    page = get_page_info(ipynb_path, conn)
    if not page:
        raise ValueError(f"No DB entry for notebook: {ipynb_path}")
    page_id = page[0]
    images = get_images_for_page(page_id, conn)
    build_dir = get_build_dir_for_file(ipynb_path)
    image_map = {}
    for img in images:
        img_id = img[0]
        img_filename = img[2]
        img_remote = img[3]
        img_filepath = img[5]
        img_url = img[6]
        img_relocated_filename = img[8]
        img_generated = bool(img[9])
        print(f"[DEBUG] Processing image: id={img_id}, filename={img_filename}, remote={img_remote}, filepath={img_filepath}, relocated={img_relocated_filename}, generated={img_generated}")
        if img_remote:
            image_map[img_url] = "REMOTE IMAGE"
        elif img_generated:
            # For code-generated images, copy using relocated filename
            src_img_path = os.path.join(build_dir, img_filename)
            dest_img_path = os.path.join(build_dir, img_relocated_filename)
            if os.path.exists(src_img_path):
                if src_img_path != dest_img_path:
                    copy_file(src_img_path, dest_img_path)
                image_map[img_filename] = img_relocated_filename
                update_image_relocated_filename(img_id, img_relocated_filename, conn)
            else:
                print(f"[WARNING] Missing code-generated image file: {src_img_path}")
                image_map[img_filename] = "MISSING IMAGE"
        else:
            # For static/markdown images, copy using original filename
            src_img_path = os.path.join(CONTENT_ROOT, img_filepath)
            dest_img_path = os.path.join(build_dir, img_filename)
            if os.path.exists(src_img_path):
                copy_file(src_img_path, dest_img_path)
                rel_img_path = os.path.relpath(dest_img_path, build_dir)
                image_map[img_filepath] = rel_img_path
                update_image_relocated_filename(img_id, rel_img_path, conn)
            else:
                print(f"[WARNING] Missing image file: {src_img_path}")
                image_map[img_filepath] = "MISSING IMAGE"
    print(f"[DEBUG] Image map: {image_map}")
    return image_map

def update_image_refs_in_markdown(md_text, image_map):
    """
    Update image references in Markdown text using the provided image map.
    """
    print(f"[DEBUG] Updating image references in markdown")
    for old, new in image_map.items():
        if new == "REMOTE IMAGE":
            md_text = md_text.replace(f"![]({old})", f"![REMOTE IMAGE]({old})")
        elif new == "MISSING IMAGE":
            md_text = md_text.replace(f"![]({old})", f"![MISSING IMAGE]({old})")
        else:
            md_text = md_text.replace(f"![]({old})", f"![]({new})")
    return md_text

# --- Notebook Execution and Conversion ---

def execute_notebook(ipynb_path, executed_path, timeout=600):
    """
    Execute a Jupyter notebook and save the executed notebook to a new file.
    """
    import nbformat
    import sys
    print(f"[DEBUG] Entered execute_notebook for {ipynb_path}")
    print(f"[DEBUG] Using Python executable: {sys.executable}")
    with open(ipynb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=timeout, kernel_name="open-physics-ed-venv")
    try:
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(ipynb_path)}})
        print(f"[DEBUG] Notebook executed successfully: {ipynb_path}")
    except Exception as e:
        print(f"[ERROR] Failed to execute notebook {ipynb_path}: {e}")
        raise
    with open(executed_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print(f"[DEBUG] Executed notebook saved at: {executed_path}")
    return executed_path

def ipynb_to_md(ipynb_path, output_path):
    """
    Convert a Jupyter notebook to Markdown, extracting images and updating references.
    Returns the path to the generated Markdown file.
    """
    print(f"[DEBUG] ipynb_to_md called for {ipynb_path} -> {output_path}")
    build_dir = get_build_dir_for_file(ipynb_path)
    executed_ipynb_path = os.path.join(build_dir, os.path.basename(ipynb_path))

    # Step 1: Execute notebook if not already present
    if not os.path.exists(executed_ipynb_path):
        print(f"[DEBUG] Executing notebook: {ipynb_path}")
        execute_notebook(ipynb_path, executed_ipynb_path)
        print(f"[DEBUG] Executed notebook saved at: {executed_ipynb_path}")
    else:
        print(f"[DEBUG] Using existing executed notebook: {executed_ipynb_path}")

    # Step 2: Get DB info
    conn = get_db_connection()
    page = get_page_info(ipynb_path, conn)
    if not page:
        print(f"[ERROR] No DB entry for notebook: {ipynb_path}")
        raise ValueError(f"No DB entry for notebook: {ipynb_path}")
    page_id = page[0]

    # Step 3: Configure nbconvert for image extraction
    c = Config()
    # Use page_id, cell_index, output_index for unique, DB-matching filenames
    c.ExtractOutputPreprocessor.output_filename_template = f'codeimg_{page_id}_{{cell_index}}_{{index}}{{extension}}'
    exporter = MarkdownExporter(config=c)
    exporter.register_preprocessor(ExtractOutputPreprocessor(), enabled=True)

    print(f"[DEBUG] Exporting notebook to Markdown: {executed_ipynb_path}")
    body, resources = exporter.from_filename(executed_ipynb_path)
    print(f"[DEBUG] resources keys: {list(resources.keys())}")
    print(f"[DEBUG] resources['outputs'] keys: {list(resources.get('outputs', {}).keys())}")

    # Step 4: Save extracted images
    outputs = resources.get('outputs', {})
    for fname, data in outputs.items():
        out_path = os.path.join(build_dir, fname)
        print(f"[DEBUG] Saving image: {out_path} ({len(data)} bytes)")
        with open(out_path, "wb") as imgf:
            imgf.write(data)

    # Step 5: Update image references in Markdown
    image_map = build_image_map(page_id, conn)
    body = update_image_refs_in_markdown(body, image_map)

    # Step 6: Write Markdown file
    if output_path is None:
        output_filename = os.path.splitext(os.path.basename(ipynb_path))[0] + ".md"
    else:
        output_filename = os.path.basename(output_path)
    md_out_path = os.path.join(build_dir, output_filename)
    print(f"[DEBUG] Writing Markdown file to: {md_out_path}")
    with open(md_out_path, "w", encoding="utf-8") as f:
        f.write(body)

    # Step 7: Update DB and log
    update_page_conversion_flag(page_id, "page_built_ok_md", conn)
    log_action(f"Converted {ipynb_path} to {md_out_path}")
    conn.close()
    print(f"[DEBUG] Markdown conversion complete for {ipynb_path}")
    return md_out_path

# --- Conversion Stubs ---

def ipynb_to_docx(ipynb_path, output_path):
    """
    Convert a Jupyter notebook to a DOCX file.
    (Currently not implemented; uses Markdown as intermediate.)
    """
    print(f"[DEBUG] ipynb_to_docx called for {ipynb_path} -> {output_path}")
    md_path = ipynb_to_md(ipynb_path, output_path.replace(".docx", ".md"))
    # Use Pandoc here (not implemented)
    pass

def ipynb_to_tex(ipynb_path, output_path):
    """
    Convert a Jupyter notebook to a LaTeX file.
    (Stub; not implemented.)
    """
    print(f"[DEBUG] ipynb_to_tex called for {ipynb_path} -> {output_path}")
    pass

def ipynb_to_pdf(ipynb_path, output_path):
    """
    Convert a Jupyter notebook to a PDF file.
    (Stub; not implemented.)
    """
    print(f"[DEBUG] ipynb_to_pdf called for {ipynb_path} -> {output_path}")
    pass

def md_to_docx(md_path, output_path):
    """
    Convert a Markdown file to a DOCX file.
    (Stub; not implemented.)
    """
    print(f"[DEBUG] md_to_docx called for {md_path} -> {output_path}")
    pass

def md_to_tex(md_path, output_path):
    """
    Convert a Markdown file to a LaTeX file.
    (Stub; not implemented.)
    """
    print(f"[DEBUG] md_to_tex called for {md_path} -> {output_path}")
    pass

def md_to_pdf(md_path, output_path):
    """
    Convert a Markdown file to a PDF file.
    (Stub; not implemented.)
    """
    print(f"[DEBUG] md_to_pdf called for {md_path} -> {output_path}")
    pass

def docx_to_md(docx_path, output_path):
    """
    Convert a DOCX file to Markdown.
    (Stub; not implemented.)
    """
    print(f"[DEBUG] docx_to_md called for {docx_path} -> {output_path}")
    pass

def docx_to_pdf(docx_path, output_path):
    """
    Convert a DOCX file to PDF.
    (Stub; not implemented.)
    """
    print(f"[DEBUG] docx_to_pdf called for {docx_path} -> {output_path}")
    pass

# End of module