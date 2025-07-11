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
    # Simple template rendering (no Jinja): replace {{ table_name }}, columns, rows
    # Render columns
    col_html = "".join(f"<th>{col}</th>" for col in columns)
    # Render rows
    row_html = "".join(
        f"<tr>{''.join(f'<td>{val}</td>' for val in row)}</tr>" for row in rows
    )
    html = template.replace("{{ table_name }}", table_name)
    html = html.replace("{% for col in columns %}<th>{{ col }}</th>{% endfor %}", col_html)
    html = html.replace("{% for row in rows %}\n      <tr>\n        {% for val in row %}<td>{{ val }}</td>{% endfor %}\n      </tr>\n      {% endfor %}", row_html)
    return html

def write_table_html(table_name, html, output_dir):
    """Write the HTML string to build/admin/{table_name}.html."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{table_name}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] Wrote {out_path}")

if __name__ == "__main__":
    import sys
    db_path = "db/sqlite.db"
    if len(sys.argv) < 2:
        print("Usage: python oerforge_admin/viewdb.py <table_name>")
        sys.exit(1)
    table_name = sys.argv[1]
    tables = get_table_names(db_path)
    if table_name not in tables:
        print(f"Table '{table_name}' not found in database. Available tables: {tables}")
        sys.exit(1)
    html = render_table_html(db_path, table_name)
    print(html)
    write_table_html(table_name, html, "build/admin")

def generate_all_table_webpages(db_path, output_dir):
    """Main function to generate a webpage for each table in the database."""
    pass
