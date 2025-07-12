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

def render_table_html(db_path, table_name):
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
    html = template.replace("{{ table_name }}", table_name).replace("{{ columns }}", col_html).replace("{{ rows }}", row_html)
    return html


def write_table_html(table_name, html, output_dir):
    """Write the HTML string to build/admin/{table_name}.html."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{table_name}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[INFO] Wrote {out_path}")

def copy_css(src_css_list, dest_css_dir):
    """Always copy all CSS files in src_css_list to build/css, overwriting if needed."""
    if not os.path.exists(dest_css_dir):
        os.makedirs(dest_css_dir, exist_ok=True)
    for src_css in src_css_list:
        dest_css = os.path.join(dest_css_dir, os.path.basename(src_css))
        shutil.copy2(src_css, dest_css)
        print(f"[INFO] Copied CSS to {dest_css}")

def generate_all_table_webpages(db_path, output_dir):
    """Generate a webpage for each table in the database and a consistent index page."""
    # Ensure all required CSS files are copied
    src_css_list = [
        os.path.join("static", "css", "theme-light.css"),
        os.path.join("static", "css", "theme-dark.css"),
    ]
    dest_css_dir = os.path.join("build", "css")
    copy_css(src_css_list, dest_css_dir)

    tables = get_table_names(db_path)
    # Generate table pages
    for table_name in tables:
        html = render_table_html(db_path, table_name)
        write_table_html(table_name, html, output_dir)
    # Generate index page using template
    template_path = os.path.join("static", "templates", "admin_index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    table_links = "\n".join(
        f"<li><a href='{table_name}.html'>{table_name}</a></li>" for table_name in tables
    )
    html = template.replace("{{ table_links }}", table_links)
    out_path = os.path.join(output_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] Wrote {out_path}")
    print(f"[INFO] Generated admin pages for tables: {tables}")

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