import os
import sqlite3
import shutil

def get_table_names(db_path):
    """Return a list of table names in the sqlite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    print("[INFO] Tables found:", tables)
    return tables

def fetch_table_data(db_path, table_name):
    """Return all rows and columns for a given table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    print(f"[INFO] Columns for table '{table_name}':", columns)
    print(f"[INFO] Number of rows: {len(rows)}")
    return columns, rows

def render_table_html(db_path, table_name, all_tables=None):
    columns, rows = fetch_table_data(db_path, table_name)
    template_path = os.path.join("static", "templates", "admin_table.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    col_html = "".join(f"<th>{col}</th>" for col in columns)

    # Detect binary columns: all values are 0 or 1
    binary_cols = set()
    for col_idx in range(len(columns)):
        col_vals = [row[col_idx] for row in rows]
        if all(val in (0, 1) for val in col_vals):
            binary_cols.add(col_idx)

    def render_cell(val, col_idx):
        if col_idx in binary_cols:
            if val == 1:
                return "✔️"
            elif val == 0:
                return "❌"
        return str(val)

    row_html = "".join(
        f"<tr>{''.join(f'<td>{render_cell(row[i], i)}</td>' for i in range(len(columns)))}</tr>" for row in rows
    )

    # Add this block to generate and insert table_links
    if all_tables is None:
        all_tables = get_table_names(db_path)
    table_links = "\n".join(
        f"<li><a href='{tbl}.html'>{tbl}</a></li>" for tbl in all_tables
    )

    html = (
        template.replace("{{ table_name }}", table_name)
                .replace("{{ columns }}", col_html)
                .replace("{{ rows }}", row_html)
                .replace("{{ table_links }}", table_links)
    )
    return html

def write_table_html(table_name, html, output_dir):
    """Write the HTML string to build/admin/{table_name}.html."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{table_name}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[INFO] Wrote {out_path}")

def copy_all_files(src_dir, dest_dir):
    """Copy all files from src_dir to dest_dir."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    for fname in os.listdir(src_dir):
        src_file = os.path.join(src_dir, fname)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, os.path.join(dest_dir, fname))
            print(f"[INFO] Copied {src_file} to {dest_dir}")
            
def render_index_html(db_path, all_tables):
    template_path = os.path.join("static", "templates", "admin_index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    table_links = "\n".join(
        f"<li><a href='{tbl}.html'>{tbl}</a></li>" for tbl in all_tables
    )
    html = template.replace("{{ table_links }}", table_links)
    return html

def generate_all_table_webpages(db_path, output_dir):
    """Generate a webpage for each table in the database and a consistent index page."""
    # Ensure output_dir exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Copy ALL CSS files to build/admin/css
    copy_all_files(os.path.join("static", "css"), os.path.join(output_dir, "css"))
    # Copy ALL JS files to build/admin/js
    copy_all_files(os.path.join("static", "js"), os.path.join(output_dir, "js"))

    tables = get_table_names(db_path)
    # Write index.html
    index_html = render_index_html(db_path, tables)
    write_table_html("index", index_html, output_dir)
    # Write table pages
    for table_name in tables:
        html = render_table_html(db_path, table_name, tables)
        write_table_html(table_name, html, output_dir)

if __name__ == "__main__":
    import sys
    db_path = "db/sqlite.db"
    if len(sys.argv) == 1:
        # No arguments: build all tables and index
        generate_all_table_webpages(db_path, "build/admin")
    elif len(sys.argv) == 2:
        table_name = sys.argv[1]
        tables = get_table_names(db_path)
        if table_name not in tables:
            print(f"Table '{table_name}' not found in database. Available tables: {tables}")
            sys.exit(1)
        html = render_table_html(db_path, table_name)
        print(html)
        write_table_html(table_name, html, "build/admin")
    else:
        print("Usage: python oerforge_admin/viewdb.py [<table_name>]")
        sys.exit(1)