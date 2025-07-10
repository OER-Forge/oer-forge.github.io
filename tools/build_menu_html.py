"""
build_menu_html.py

Script to generate the HTML <nav> menu for the site, matching the structure and output of the current index.html navigation.
- Uses menu_parser.get_menu_tree to extract the validated menu structure from _content.yml.
- Outputs a single HTML <ul> structure suitable for direct inclusion in index.html or other templates.
- Recursively builds dropdowns for children.
- Converts .md/.ipynb to .html for links.
- Prints the HTML to stdout.

Usage:
    python build_menu_html.py > menu.html
"""
from menu_parser import get_menu_tree
import os

def file_to_html_link(file_path, title):
    base, ext = os.path.splitext(os.path.basename(file_path))
    return f'<a href="{base}.html">{title}</a>'

def build_menu_ul(menu, level=0):
    html = []
    ul_class = 'site-nav-menu' if level == 0 else f'dropdown-menu menu-level-{level}'
    html.append(f'<ul class="{ul_class}">')
    for item in menu:
        title = item['title']
        file = item.get('file')
        children = item.get('children')
        html.append('<li>')
        if file:
            html.append(file_to_html_link(file, title))
        else:
            html.append(f'<span>{title}</span>')
        if children:
            html.append(build_menu_ul(children, level+1))
        html.append('</li>')
    html.append('</ul>')
    return ''.join(html)

if __name__ == '__main__':
    menu = get_menu_tree('_content.yml')
    html = build_menu_ul(menu)
    print(html)
