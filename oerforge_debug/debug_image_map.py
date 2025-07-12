import sys
import sqlite3

def debug_image_map(db_path, ipynb_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Find page_id for the notebook
    cursor.execute("SELECT page_id FROM page WHERE page_filename=?", (ipynb_path.split('/')[-1],))
    result = cursor.fetchone()
    if not result:
        print(f"[ERROR] No page found for {ipynb_path}")
        return
    page_id = result[0]
    # Get image mapping
    cursor.execute("SELECT image_filename, image_relocated_filename FROM page_images WHERE image_page_id=?", (page_id,))
    mapping = {row[0]: row[1] for row in cursor.fetchall()}
    print(f"[DEBUG] Image mapping for page_id={page_id}:")
    for k, v in mapping.items():
        print(f"  {k} -> {v}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python oerforge_debug/debug_image_map.py <db_path> <ipynb_path>")
        sys.exit(1)
    debug_image_map(sys.argv[1], sys.argv[2])