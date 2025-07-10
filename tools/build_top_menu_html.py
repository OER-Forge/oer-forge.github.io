"""
build_top_menu_html.py

Script to generate the top-level HTML <ul> menu for the site, with no submenus.
- Uses menu_parser.get_menu_tree to extract the validated menu structure from _content.yml.
- Outputs a single HTML <ul> structure with only top-level menu items (no dropdowns).
- Converts .md/.ipynb to .html for links.
- Prints the HTML to stdout.

Usage:
    python build_top_menu_html.py > top_menu.html
"""
from menu_parser import get_menu_tree
import os

def file_to_html_link(file_path, title):
    base, ext = os.path.splitext(os.path.basename(file_path))
    return f'<a href="{base}.html">{title}</a>'

if __name__ == '__main__':
    menu = get_menu_tree('_content.yml')
    html = ['<ul class="site-nav-menu" id="site-nav-menu">']
    for item in menu:
        title = item['title']
        file = item.get('file')
        html.append('<li>')
        if file:
            html.append(file_to_html_link(file, title))
        else:
            html.append(f'<span>{title}</span>')
        html.append('</li>')
    html.append('</ul>')
    print(''.join(html))
