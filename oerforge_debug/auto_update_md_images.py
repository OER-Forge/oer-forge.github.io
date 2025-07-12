import sys
import os
import sqlite3
import re

def get_page_id(db_path, ipynb_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    notebook_filename = os.path.basename(ipynb_path)
    cursor.execute("SELECT page_id FROM page WHERE page_filename=?", (notebook_filename,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        print(f"[ERROR] No page found for {ipynb_path} (filename: {notebook_filename})")
        return None
    return result[0]

def get_image_mapping(db_path, page_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT image_filename, image_relocated_filename FROM page_images WHERE image_page_id=?", (page_id,))
    mapping = dict(cursor.fetchall())
    conn.close()
    return mapping

def notebook_to_markdown_path(ipynb_path):
    # Replace 'content/' with 'build/files/' and '.ipynb' with '.md'
    if ipynb_path.startswith("content/"):
        md_path = "build/files/" + ipynb_path[len("content/"):]
    else:
        md_path = ipynb_path
    md_path = md_path.rsplit(".ipynb", 1)[0] + ".md"
    return md_path

def replace_images_in_markdown(md_path, image_map):
    if not os.path.isfile(md_path):
        print(f"[ERROR] Markdown file not found: {md_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    changes = []
    def replacer(match):
        fname = match.group(0)
        new_fname = image_map.get(fname)
        if new_fname:
            changes.append((fname, new_fname))
            return new_fname
        return fname

    new_md_text = re.sub(r'output_[0-9_]+\.png', replacer, md_text)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(new_md_text)

    print(f"[OK] Updated image references in {md_path}")
    if changes:
        print("Replacements made:")
        for old, new in changes:
            print(f"  {old} -> {new}")
    else:
        print("No replacements made. Check your DB mapping and markdown file.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python oerforge_debug/auto_update_md_images.py <db_path> <ipynb_path>")
        sys.exit(1)
    db_path = sys.argv[1]
    ipynb_path = sys.argv[2]

    page_id = get_page_id(db_path, ipynb_path)
    if page_id is None:
        sys.exit(1)
    image_map = get_image_mapping(db_path, page_id)
    md_path = notebook_to_markdown_path(ipynb_path)
    replace_images_in_markdown(md_path, image_map)