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

from db_utils import log_event

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
BUILD_ROOT = "build/files"
LOG_DIR = "log"

# --- Logging Utility ---
# Use log_event from db_utils.py for all logging

# --- Image Handling Utility ---
def copy_and_update_images_for_file(content_record, conn):
    """
    Copy all images associated with a file (from content_record) to the build directory.
    Update image references in converted files as needed.
    Use image info from sqlite.db (e.g., page_images table).
    """
    # TODO: Query image info from DB, copy images, update references in output files
    log_event(f"[STUB] Copying/updating images for {content_record['source_path']}", level="DEBUG")
    pass

# --- Conversion Stubs ---
def convert_ipynb_to_md(content_record, conn):
    """
    Convert a Jupyter notebook (.ipynb) to Markdown (.md).
    Copy original file to build/files. Extract and copy images. Update DB conversion status.
    """
    log_event(f"[STUB] Converting ipynb to md for {content_record['source_path']}", level="DEBUG")
    pass

def convert_docx_to_md(content_record, conn):
    """
    Convert a DOCX file to Markdown (.md).
    Copy original file to build/files. Extract and copy images. Update DB conversion status.
    """
    log_event(f"[STUB] Converting docx to md for {content_record['source_path']}", level="DEBUG")
    pass

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
            # Copy original file to build/files (mirroring TOC hierarchy)
            # TODO: Implement TOC-based directory structure
            # Conversion logic
            if content_record.get('can_convert_md'):
                if src_path.endswith('.ipynb'):
                    convert_ipynb_to_md(content_record, conn)
                elif src_path.endswith('.docx'):
                    convert_docx_to_md(content_record, conn)
            # Once .md exists, convert to other formats as flagged
            if src_path.endswith('.md') or content_record.get('can_convert_md'):
                if content_record.get('can_convert_docx'):
                    convert_md_to_docx(content_record, conn)
                if content_record.get('can_convert_pdf'):
                    convert_md_to_pdf(content_record, conn)
                if content_record.get('can_convert_tex'):
                    convert_md_to_tex(content_record, conn)
            # Image handling
            copy_and_update_images_for_file(content_record, conn)
        conn.close()
    except Exception as e:
        log_event(f"Batch conversion failed: {e}", level="ERROR")

# --- Main Entry Point ---
if __name__ == "__main__":
    log_event("[convert] __main__ entry: running batch_convert_all_content()", level="INFO")
    batch_convert_all_content()

