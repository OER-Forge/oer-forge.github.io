"""
export_db_html.py: Export asset DB tables to static HTML using site templates (e.g., page.html).
"""
import os
from tabulate import tabulate
from view_db import get_db_path, get_table_names, get_table_columns, fetch_table

def render_table_html(table_name, columns=None, where=None, limit=None):
    cols = columns if columns else get_table_columns(table_name)
    rows = fetch_table(table_name, columns=columns, where=where, limit=limit)
    return tabulate(rows, headers=cols, tablefmt="html")

def inject_table_into_template(table_html, template_path, output_path):
    """
    Read template, inject table_html at <!-- ASSET_TABLE -->, write to output_path.
    """
    with open(template_path, "r") as f:
        template = f.read()
    html = template.replace("<!-- ASSET_TABLE -->", table_html)
    with open(output_path, "w") as f:
        f.write(html)

def export_table_to_html(table_name, output_path, template_path=None, columns=None, where=None, limit=None):
    """
    Export a table to static HTML using a site template.
    """
    if not template_path:
        # Default to page.html in static/templates
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(project_root, "static", "templates", "page.html")
    table_html = render_table_html(table_name, columns, where, limit)
    inject_table_into_template(table_html, template_path, output_path)

def export_all_tables_to_html(output_dir, template_path=None):
    """
    Export all tables to static HTML files in output_dir using a site template.
    """
    os.makedirs(output_dir, exist_ok=True)
    for table in get_table_names():
        output_path = os.path.join(output_dir, f"{table}_table.html")
        export_table_to_html(table, output_path, template_path)

if __name__ == "__main__":
    # Example usage stub
    # export_table_to_html("files", "static/admin_index.html")
    # export_all_tables_to_html("static/admin_tables/")
    print("Run as a module or import for use in build/make workflow.")
