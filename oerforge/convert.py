import os
import shutil
import sqlite3
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExtractOutputPreprocessor
from traitlets.config import Config

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "sqlite.db")
CONTENT_ROOT = "content"
BUILD_ROOT = "build/files"
LOG_DIR = "log"

def get_db_connection(db_path=DB_PATH):
    return sqlite3.connect(db_path)

def get_page_info(full_path, conn):
    # Split into directory and filename
    dir_path, filename = os.path.split(full_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM page WHERE page_filepath=? AND page_filename=?",
        (dir_path, filename)
    )
    return cursor.fetchone()

def get_images_for_page(page_id, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM page_images WHERE image_page_id=?", (page_id,))
    return cursor.fetchall()

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def copy_file(src, dest):
    ensure_dir(os.path.dirname(dest))
    shutil.copy2(src, dest)

def log_action(message):
    ensure_dir(LOG_DIR)
    log_path = os.path.join(LOG_DIR, "convert.log")
    with open(log_path, "a") as logf:
        logf.write(message + "\n")

def get_build_dir_for_file(src_path):
    rel_dir = os.path.relpath(os.path.dirname(src_path), CONTENT_ROOT)
    build_dir = os.path.join(BUILD_ROOT, rel_dir)
    ensure_dir(build_dir)
    return build_dir

def update_image_relocated_filename(img_id, new_path, conn):
    cursor = conn.cursor()
    cursor.execute("UPDATE page_images SET image_relocated_filename=? WHERE id=?", (new_path, img_id))
    conn.commit()

def update_page_conversion_flag(page_id, flag, conn):
    cursor = conn.cursor()
    cursor.execute(f"UPDATE page SET {flag}=1 WHERE page_id=?", (page_id,))
    conn.commit()
    # Debug: print the updated value
    cursor.execute(f"SELECT {flag} FROM page WHERE page_id=?", (page_id,))
    print(f"[DEBUG] {flag} for page_id {page_id} is now:", cursor.fetchone())

def copy_images_for_ipynb(ipynb_path, conn=None):
    """
    Copies all images referenced by a notebook (from the page_images table) to the build/files/ directory,
    preserving the user's organization. Checks if the image file exists and handles missing files gracefully.
    Returns a dict mapping original image paths to new relative paths or status.
    """
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
        if img_remote:
            image_map[img_filepath] = "REMOTE IMAGE"
        else:
            src_img_path = os.path.join(CONTENT_ROOT, img_filepath)
            dest_img_path = os.path.join(build_dir, img_filename)
            if os.path.exists(src_img_path):
                copy_file(src_img_path, dest_img_path)
                rel_img_path = os.path.relpath(dest_img_path, build_dir)
                image_map[img_filepath] = rel_img_path
                update_image_relocated_filename(img_id, rel_img_path, conn)
            else:
                image_map[img_filepath] = "MISSING IMAGE"
    return image_map

def update_image_refs_in_markdown(md_text, image_map):
    """
    Replace image references in markdown text using image_map.
    """
    for old, new in image_map.items():
        if new == "REMOTE IMAGE":
            md_text = md_text.replace(f"![]({old})", f"![REMOTE IMAGE]({old})")
        elif new == "MISSING IMAGE":
            md_text = md_text.replace(f"![]({old})", f"![MISSING IMAGE]({old})")
        else:
            md_text = md_text.replace(f"![]({old})", f"![]({new})")
    return md_text

def ipynb_to_md(ipynb_path, output_path):
    conn = get_db_connection()
    page = get_page_info(ipynb_path, conn)
    if not page:
        raise ValueError(f"No DB entry for notebook: {ipynb_path}")
    page_id = page[0]
    build_dir = get_build_dir_for_file(ipynb_path)

    # Configure nbconvert to extract images
    c = Config()
    c.ExtractOutputPreprocessor.output_filename_template = os.path.join(build_dir, '{unique_key}_{cell_index}_{index}{extension}')
    exporter = MarkdownExporter(config=c)
    exporter.register_preprocessor(ExtractOutputPreprocessor(), enabled=True)

    body, resources = exporter.from_filename(ipynb_path)

    # Optionally, update image references in markdown if needed
    # (nbconvert should handle this, but you can post-process if you want custom paths)
    # body = update_image_refs_in_markdown(body, image_map)

    if output_path is None:
        output_filename = os.path.splitext(os.path.basename(ipynb_path))[0] + ".md"
    else:
        output_filename = os.path.basename(output_path)
    md_out_path = os.path.join(build_dir, output_filename)
    with open(md_out_path, "w", encoding="utf-8") as f:
        f.write(body)
    copy_file(ipynb_path, os.path.join(build_dir, os.path.basename(ipynb_path)))
    update_page_conversion_flag(page_id, "page_built_ok_md", conn)
    log_action(f"Converted {ipynb_path} to {md_out_path}")
    conn.close()
    return md_out_path

# Other converters can use these helpers:
# - get_db_connection
# - get_page_info
# - get_images_for_page
# - get_build_dir_for_file
# - copy_file
# - log_action
# - update_image_refs_in_markdown
# - update_page_conversion_flag
# - copy_images_for_ipynb

def ipynb_to_docx(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a DOCX file using nbconvert and Pandoc."""
    print(f"[DEBUG] ipynb_to_md called for {ipynb_path} -> {output_path}")
    # Example: convert to markdown first, then use Pandoc to convert to docx
    md_path = ipynb_to_md(ipynb_path, output_path.replace(".docx", ".md"))
    # Use Pandoc here (not implemented)
    pass

def ipynb_to_tex(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a LaTeX file."""
    # Use nbconvert or Pandoc as needed
    pass

def ipynb_to_pdf(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a PDF file."""
    # Use nbconvert or Pandoc as needed
    pass

def md_to_docx(md_path, output_path):
    """Convert a Markdown file (.md) to a DOCX file."""
    # Use Pandoc
    pass

def md_to_tex(md_path, output_path):
    """Convert a Markdown file (.md) to a LaTeX file."""
    # Use Pandoc
    pass

def md_to_pdf(md_path, output_path):
    """Convert a Markdown file (.md) to a PDF file."""
    # Use Pandoc
    pass

def docx_to_md(docx_path, output_path):
    """Convert a DOCX file to a Markdown file (.md)."""
    # Use Pandoc
    pass

def docx_to_pdf(docx_path, output_path):
    """Convert a DOCX file to a PDF file."""
    # Use Pandoc
    pass