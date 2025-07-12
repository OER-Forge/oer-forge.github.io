import sys
import sqlite3
import re
import os

def get_image_map(db_path, ipynb_path):
    """
    Retrieve a mapping of image filenames to their relocated filenames for a given notebook.

    Args:
        db_path (str): Path to the SQLite database file.
        ipynb_path (str): Path to the Jupyter notebook file.

    Returns:
        dict: Mapping from original image filenames to relocated image filenames.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Get the page_id for the notebook
        cursor.execute(
            "SELECT page_id FROM page WHERE page_filename=?",
            (os.path.basename(ipynb_path),)
        )
        result = cursor.fetchone()
        if not result:
            print(f"[ERROR] No page found for {ipynb_path}")
            return {}
        page_id = result[0]
        # Get image filename mappings for the page
        cursor.execute(
            "SELECT image_filename, image_relocated_filename FROM page_images WHERE image_page_id=?",
            (page_id,)
        )
        image_map = dict(cursor.fetchall())
        return image_map
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def update_md_images(md_path, image_map):
    """
    Update image references in a Markdown file using a provided mapping.

    Args:
        md_path (str): Path to the Markdown file.
        image_map (dict): Mapping from original image filenames to relocated filenames.

    Returns:
        None
    """
    if not os.path.isfile(md_path):
        print(f"[ERROR] Markdown file not found: {md_path}")
        return

    try:
        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"[ERROR] Failed to read {md_path}: {e}")
        return

    # Replace image references in markdown: ![png](output_4_0.png) -> ![png](codeimg_...png)
    def replacer(match):
        orig_fname = match.group(1)
        new_fname = image_map.get(orig_fname, orig_fname)
        return f"![png]({new_fname})"

    # This regex matches markdown image references with output_*.png
    new_md_text = re.sub(r'!\[png\]\((output_[0-9_]+\.png)\)', replacer, md_text)

    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(new_md_text)
        print(f"[OK] Updated image references in {md_path}")
    except OSError as e:
        print(f"[ERROR] Failed to write {md_path}: {e}")

def notebook_to_markdown_path(ipynb_path):
    """
    Convert a notebook path to its corresponding Markdown file path.

    Args:
        ipynb_path (str): Path to the Jupyter notebook file.

    Returns:
        str: Path to the corresponding Markdown file.
    """
    # Replace 'content/' with 'build/files/' and change extension to '.md'
    if ipynb_path.startswith("content/"):
        md_path = "build/files/" + ipynb_path[len("content/"):]
    else:
        md_path = ipynb_path
    md_path = md_path.rsplit(".ipynb", 1)[0] + ".md"
    return md_path

def main():
    """
    Main entry point for the script. Validates arguments and updates Markdown image references.
    """
    if len(sys.argv) != 3:
        print("Usage: python oerforge_debug/update_md_images_with_db.py <db_path> <ipynb_path>")
        sys.exit(1)
    db_path = sys.argv[1]
    ipynb_path = sys.argv[2]
    md_path = notebook_to_markdown_path(ipynb_path)
    image_map = get_image_map(db_path, ipynb_path)
    if image_map:
        update_md_images(md_path, image_map)

if __name__ == "__main__":
    main()