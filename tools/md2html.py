#!/usr/bin/env python3
"""
md2html.py - Convert all .md files in content/notebooks (and subfolders) to HTML files in-place (next to the .md file).

Usage:
    python scripts/md2html.py

This script will:
- Recursively find all .md files in content/notebooks
- Convert each to HTML using Python's markdown library
- Write the HTML file as <basename>.md.html next to the original .md file
- Print a summary of conversions
"""
import os
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("[ERROR] The 'markdown' package is required. Install with: pip install markdown", file=sys.stderr)
    sys.exit(1)

def convert_md_to_html(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content, extensions=['extra', 'toc', 'tables'])
    # Remove all suffixes and add .html (e.g., intro.md -> intro.html)
    html_path = md_path
    while html_path.suffix:
        html_path = html_path.with_suffix('')
    html_path = html_path.with_suffix('.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return html_path

def main():
    notebooks_dir = Path('content/notebooks')
    if not notebooks_dir.exists():
        print(f"[ERROR] Directory not found: {notebooks_dir}")
        sys.exit(1)
    md_files = list(notebooks_dir.rglob('*.md'))
    if not md_files:
        print("[INFO] No markdown files found.")
        return
    print(f"[INFO] Found {len(md_files)} markdown files. Converting to HTML...")
    converted = []
    for md_file in md_files:
        html_file = convert_md_to_html(md_file)
        print(f"[OK] {md_file} -> {html_file}")
        converted.append((md_file, html_file))
    print(f"[DONE] Converted {len(converted)} markdown files to HTML.")

if __name__ == '__main__':
    main()
