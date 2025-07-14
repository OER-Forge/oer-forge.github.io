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

from oerforge.db_utils import log_event, get_records

import sys
import os
import shutil
import sqlite3
import subprocess
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor, ExtractOutputPreprocessor
from traitlets.config import Config
import re

# --- Constants ---
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "sqlite.db")
CONTENT_ROOT = "content"
BUILD_ROOT = "build/images"
IMAGES_ROOT = "images"  # Top-level images directory for all copied images
LOG_DIR = "log"

# --- Modular Image Handling for Markdown ---
def query_images_for_content(content_record, conn):
    """
    Query sqlite.db for all images associated with this content file.
    Returns a list of image records (dicts).
    """
    from oerforge.db_utils import get_records
    images = get_records(
        "files",
        "is_image=1 AND referenced_page=?",
        (content_record['source_path'],),
        conn=conn
    )
    log_event(f"[IMAGES] Found {len(images)} images for {content_record['source_path']}", level="DEBUG")
    return images

def copy_images_to_build(images, images_root=IMAGES_ROOT):
    """
    Copy each image to the top-level images directory. All images go in images/ with their filename only.
    Returns a list of new build paths (absolute paths).
    """
    os.makedirs(images_root, exist_ok=True)
    copied = []
    for img in images:
        src = img.get('relative_path') or img.get('absolute_path')
        log_event(f"[IMAGES][DEBUG] src={src} img={img}", level="DEBUG")
        if not src or img.get('is_remote'):
            log_event(f"[IMAGES] Skipping remote or missing image: {img.get('filename')}", level="WARNING")
            continue
        filename = os.path.basename(src)
        dest = os.path.join(images_root, filename)
        log_event(f"[IMAGES][DEBUG] Copying {src} to {dest}", level="DEBUG")
        try:
            shutil.copy2(src, dest)
            log_event(f"[IMAGES] Copied image {src} to {dest}", level="INFO")
            copied.append(dest)
        except Exception as e:
            log_event(f"[IMAGES] Failed to copy {src} to {dest}: {e}", level="ERROR")
    return copied

def update_markdown_image_links(md_path, images, images_root=IMAGES_ROOT):
    """
    Update image links in the Markdown file to point to the copied images in the top-level images directory.
    """
    if not os.path.exists(md_path):
        log_event(f"[IMAGES] Markdown file not found: {md_path}", level="WARNING")
        return
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Replace all image links to use images/<filename> relative to the markdown file
    for img in images:
        src = img.get('relative_path') or img.get('absolute_path')
        if not src:
            continue
        filename = os.path.basename(src)
        new_path = f'images/{filename}'
        # Replace any markdown image link that references this filename, regardless of subfolder
        pattern = r'(!\[[^\]]*\]\()([^)]*' + re.escape(filename) + r')\)'
        replacement = r'\1' + new_path + r')'
        log_event(f"[IMAGES][DEBUG] Updating markdown links for {filename}: pattern={pattern} replacement={replacement}", level="DEBUG")
        content = re.sub(pattern, replacement, content)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    log_event(f"[IMAGES] Updated image links in {md_path}", level="INFO")

def handle_images_for_markdown(content_record, conn):
    """
    Orchestrate image handling for a Markdown file: query, copy, update links.
    """
    images = query_images_for_content(content_record, conn)
    copied = copy_images_to_build(images)
    rel_path = os.path.relpath(content_record['source_path'], CONTENT_ROOT)
    md_path = os.path.join(BUILD_ROOT, rel_path)
    update_markdown_image_links(md_path, images)
    log_event(f"[IMAGES] Finished handling images for {md_path}", level="INFO")
    
def convert_md_to_docx(content_record, conn):
    """
    Convert a Markdown file to DOCX using Pandoc.
    Copy converted file to build/files. Update DB conversion status.
    """
    src_path = content_record['source_path']
    print(f"[DEBUG] Starting Markdown to DOCX conversion for: {src_path}")
    # Determine output path: change extension to .docx, mirror TOC hierarchy
    rel_path = os.path.relpath(src_path, CONTENT_ROOT)
    out_path = os.path.join(BUILD_ROOT, os.path.splitext(rel_path)[0] + '.docx')
    print(f"[DEBUG] Output DOCX path: {out_path}")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    abs_src_path = os.path.join(CONTENT_ROOT, rel_path)
    # Copy original .md to build/files if not already there
    build_md_path = os.path.join(BUILD_ROOT, rel_path)
    print(f"[DEBUG] Build Markdown path: {build_md_path}")
    if not os.path.exists(build_md_path):
        try:
            shutil.copy2(abs_src_path, build_md_path)
            print(f"[DEBUG] Copied original md to {build_md_path}")
            log_event(f"Copied original md to {build_md_path}", level="INFO")
        except Exception as e:
            print(f"[ERROR] Failed to copy md: {e}")
            log_event(f"Failed to copy md: {e}", level="ERROR")
            return
    # Run Pandoc to convert md to docx
    try:
        print(f"[DEBUG] Running Pandoc: pandoc {build_md_path} -o {out_path}")
        subprocess.run([
            "pandoc",
            build_md_path,
            "-o",
            out_path
        ], check=True)
        print(f"[DEBUG] Converted {build_md_path} to DOCX at {out_path}")
        log_event(f"Converted {build_md_path} to DOCX at {out_path}", level="INFO")
        # Update DB: set converted_docx = 1 for this record
        cursor = conn.cursor()
        cursor.execute("UPDATE content SET converted_docx=1 WHERE id=?", (content_record['id'],))
        conn.commit()
        print(f"[DEBUG] DB updated: converted_docx=1 for id {content_record['id']}")
        log_event(f"DB updated: converted_docx=1 for id {content_record['id']}", level="INFO")
    except Exception as e:
        print(f"[ERROR] Pandoc conversion failed: {e}")
        log_event(f"Pandoc conversion failed: {e}", level="ERROR")

def convert_md_to_pdf(content_record, conn):
    """
    Convert a Markdown file to PDF using Pandoc.
    Copy converted file to build/files. Update DB conversion status.
    """
    log_event(f"[STUB] Converting md to pdf for {content_record['source_path']}", level="DEBUG")
    pass

def convert_md_to_tex(content_record, conn):
    """
    Convert a Markdown file to LaTeX using Pandoc.
    Copy converted file to build/files. Update DB conversion status.
    """
    log_event(f"[STUB] Converting md to tex for {content_record['source_path']}", level="DEBUG")
    pass

# --- Batch Conversion Orchestrator ---
def batch_convert_all_content():
    """
    Main entry point: batch process all files in the content table.
    For each file, check conversion flags and call appropriate conversion stubs.
    Copy original files to build/files. Organize output to mirror TOC hierarchy.
    Log all errors and warnings to log/convert.log.
    """
    print("[DEBUG] Starting batch conversion for all content records.")
    log_event("Starting batch conversion for all content records.", level="INFO")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM content")
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            content_record = dict(zip(columns, row))
            src_path = content_record['source_path']
            print(f"[DEBUG] Processing {src_path}")
            log_event(f"Processing {src_path}", level="INFO")
            # Only handle images for markdown files for now
            if src_path.endswith('.md'):
                handle_images_for_markdown(content_record, conn)
        conn.close()
    except Exception as e:
        log_event(f"Batch conversion failed: {e}", level="ERROR")

# --- Main Entry Point ---
if __name__ == "__main__":
    log_event("[convert] __main__ entry: running batch_convert_all_content()", level="INFO")
    batch_convert_all_content()

