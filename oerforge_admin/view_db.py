"""
view_db.py: CLI/utility for viewing asset database contents (files/pages_files only).
Intended for future web admin interface.
"""
import os
import sqlite3
from tabulate import tabulate

def get_db_path():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, 'db', 'sqlite.db')

def get_table_names():
    """
    Return only the asset DB tables: files and pages_files.
    """
    return ['files', 'pages_files']

def get_table_columns(table_name):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return columns

def fetch_table(table_name, columns=None, where=None, limit=None):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cols = ', '.join(columns) if columns else '*'
    query = f"SELECT {cols} FROM {table_name}"
    if where:
        query += f" WHERE {where}"
    if limit:
        query += f" LIMIT {limit}"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def display_table(table_name, columns=None, where=None, limit=None):
    cols = columns if columns else get_table_columns(table_name)
    rows = fetch_table(table_name, columns=columns, where=where, limit=limit)
    print(f"\nTable: {table_name}")
    print(tabulate(rows, headers=cols, tablefmt="grid"))

def display_all_tables():
    for table in get_table_names():
        display_table(table)


# --- Stubs for static HTML export and template integration ---
def export_table_to_html(table_name, output_path, template_path=None, columns=None, where=None, limit=None):
    """
    Stub: Export a table to static HTML using a site template.
    - table_name: DB table to export
    - output_path: Path to write HTML file
    - template_path: Optional path to HTML template (from static/templates)
    - columns, where, limit: Optional query params
    """
    # TODO: Query table, render as HTML table, inject into template, write to output_path
    pass

def export_all_tables_to_html(output_dir, template_path=None):
    """
    Stub: Export all tables to static HTML files in output_dir using a site template.
    """
    # TODO: Loop over tables, call export_table_to_html for each
    pass

def integrate_with_make():
    """
    Stub: Integrate admin HTML export into build/make process.
    """
    # TODO: Hook export functions into make.py/build.py workflow
    pass

    import argparse
    parser = argparse.ArgumentParser(description="View asset database contents (files/pages_files only).")
    parser.add_argument('--table', type=str, choices=get_table_names(), help='Table name to display (files or pages_files)')
    parser.add_argument('--columns', type=str, nargs='+', help='Columns to display')
    parser.add_argument('--where', type=str, help='SQL WHERE clause')
    parser.add_argument('--limit', type=int, help='Limit number of rows')
    parser.add_argument('--all', action='store_true', help='Display both files and pages_files tables')
    # Future: parser.add_argument('--export-html', action='store_true', help='Export table(s) to static HTML')
    args = parser.parse_args()

    if args.all:
        display_all_tables()
    elif args.table:
        display_table(args.table, columns=args.columns, where=args.where, limit=args.limit)
    else:
        print("Specify --table files, --table pages_files, or --all to display asset database contents.")

if __name__ == "__main__":
    main()

"""
Recommendations for future web admin interface:
- Use this module's logic as backend for a Flask/FastAPI app.
- Provide endpoints for table listing, selective queries, and pagination.
- Use tabulate or pandas for pretty HTML tables.
- Add authentication and role-based access for admin features.
- Support export to CSV/JSON for data analysis.
- Add search/filter UI for large tables.
- Only expose files and pages_files tables for asset management.
"""
