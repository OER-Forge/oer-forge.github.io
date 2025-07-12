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

def build_output_to_codeimg_map(db_path, page_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT image_generated_cell_index, image_generated_output_index, image_relocated_filename
        FROM page_images
        WHERE image_page_id=?
    """, (page_id,))
    mapping = {}
    for cell_idx, out_idx, relocated in cursor.fetchall():
        if cell_idx is not None and out_idx is not None and relocated:
            output_fname = f"output_{cell_idx}_{out_idx}.png"
            mapping[output_fname] = relocated
    conn.close()
    return mapping

def notebook_to_markdown_path(ipynb_path):
    if ipynb_path.startswith("content/"):
        md_path = "build/files/" + ipynb_path[len("content/"):]
    else:
        md_path = ipynb_path
    md_path = md_path.rsplit(".ipynb", 1)[0] + ".md"
    return md_path

def patch_markdown(md_path, image_map):
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

    new_md_path = md_path.replace(".md", ".patched.md")
    with open(new_md_path, "w", encoding="utf-8") as f:
        f.write(new_md_text)

    if changes:
        # Overwrite the original file if replacements were made
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(new_md_text)
        print(f"[OK] Replacements made. Original markdown file updated: {md_path}")
    else:
        print(f"[INFO] No replacements made. Patched file left at: {new_md_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python oerforge_debug/patch_md_output_images.py <db_path> <ipynb_path>")
        sys.exit(1)
    db_path = sys.argv[1]
    ipynb_path = sys.argv[2]

    page_id = get_page_id(db_path, ipynb_path)
    if page_id is None:
        sys.exit(1)
    image_map = build_output_to_codeimg_map(db_path, page_id)
    md_path = notebook_to_markdown_path(ipynb_path)
    patch_markdown(md_path, image_map)