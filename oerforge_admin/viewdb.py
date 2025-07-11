import os
import sqlite3

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
    """Render HTML for a table using the static template and WCAG-compliant CSS."""
    columns, rows = fetch_table_data(db_path, table_name)
    template_path = os.path.join("static", "templates", "admin_table.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    # Simple template rendering: replace {{ table_name }}, {{ columns }}, {{ rows }}
    col_html = "".join(f"<th>{col}</th>" for col in columns)
    row_html = "".join(
        f"<tr>{''.join(f'<td>{val}</td>' for val in row)}</tr>" for row in rows
    )
    html = template.replace("{{ table_name }}", table_name)
    html = html.replace("{{ columns }}", col_html)
    html = html.replace("{{ rows }}", row_html)
    return html

def write_table_html(table_name, html, output_dir):
    """Write the HTML string to build/admin/{table_name}.html."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{table_name}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[INFO] Wrote {out_path}")

def generate_all_table_webpages(db_path, output_dir):
    """Generate a webpage for each table in the database."""
    tables = get_table_names(db_path)
    # Generate table pages
    for table_name in tables:
        html = render_table_html(db_path, table_name)
        write_table_html(table_name, html, output_dir)
    # Generate index page with links to all tables
    index_html = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <title>Database Tables</title>",
        "  <link id='theme-css' rel='stylesheet' href='../css/admin-light.css'>",
        "</head>",
        "<body>",
        "  <div class='theme-switcher' style='text-align:right; margin-bottom:1em;'>",
        "    <button id='theme-toggle' aria-label='Switch theme' style='padding:0.5em 1em; font-weight:700; border-radius:6px; border:2px solid #1a237e; background:#e0e7ef; color:#1a237e; cursor:pointer;'>Switch to Dark Mode</button>",
        "  </div>",
        "  <div class='container'>",
        "    <h1>Database Tables</h1>",
        "    <nav aria-label='Admin Table Navigation'>",
        "      <ul class='admin-menu'>"
    ]
    for table_name in tables:
        index_html.append(f"        <li><a href='{table_name}.html'>{table_name}</a></li>")
    index_html.extend([
        "      </ul>",
        "    </nav>",
        "  </div>",
        "</body>",
        "</html>"
    ])
    out_path = os.path.join(output_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(index_html))
    print(f"[INFO] Wrote {out_path}")
    print(f"[INFO] Generated admin pages for tables: {tables}")

if __name__ == "__main__":
    import sys
    db_path = "db/sqlite.db"
    if len(sys.argv) == 2 and sys.argv[1] == "--all":
        generate_all_table_webpages(db_path, "build/admin")
    elif len(sys.argv) >= 2:
        table_name = sys.argv[1]
        tables = get_table_names(db_path)
        if table_name not in tables:
            print(f"Table '{table_name}' not found in database. Available tables: {tables}")
            sys.exit(1)
        html = render_table_html(db_path, table_name)
        print(html)
        write_table_html(table_name, html, "build/admin")
    else:
        print("Usage: python oerforge_admin/viewdb.py <table_name> | --all")
        sys.exit(1)

def generate_all_table_webpages(db_path, output_dir):
    """Main function to generate a webpage for each table in the database."""
    pass
