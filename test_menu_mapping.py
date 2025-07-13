import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filename='test_menu_mapping.log', filemode='w')

# Simulated top-level menu items and their HTML locations
menus = {
    "Home": "build/index.html",
    "Docs": "build/docs/index.html",
    "Dev": "build/dev/index.html",
    "About": "build/about.html"
}

# Simulated fake HTML files in various subdirectories
fake_html_files = [
    "build/index.html",
    "build/docs/index.html",
    "build/docs/subsection/page.html",
    "build/dev/index.html",
    "build/dev/sub/page.html",
    "build/about.html",
    "build/docs/extra/notes.html"
]

print("[TEST] Mapping menu links from fake HTML files to top-level menu items")
for fake_html in fake_html_files:
    current_dir = os.path.dirname(fake_html)
    print(f"\n[DEBUG] Fake HTML file: {fake_html} (dir: {current_dir})")
    logging.debug(f"Fake HTML file: {fake_html} (dir: {current_dir})")
    for menu_name, menu_html in menus.items():
        rel_link = os.path.relpath(menu_html, start=current_dir)
        debug_msg = f"Menu: {menu_name}, Top-level HTML: {menu_html}, Link from {fake_html}: {rel_link}"
        print(debug_msg)
        logging.debug(debug_msg)
