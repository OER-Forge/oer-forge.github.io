
import os

def find_menu_pages(build_dir):
    menu_pages = []
    # Top-level .html files
    for entry in os.listdir(build_dir):
        path = os.path.join(build_dir, entry)
        if os.path.isfile(path) and entry.endswith('.html'):
            menu_pages.append(path)
        elif os.path.isdir(path):
            index_html = os.path.join(path, 'index.html')
            if os.path.isfile(index_html):
                menu_pages.append(index_html)
    return sorted(menu_pages)

def test_menu_links():
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filename='test_menu_links.log', filemode='w')
    build_dir = 'build'
    menu_pages = find_menu_pages(build_dir)
    print("[TEST] Menu link computation for all menu pages")
    print(f"Found menu pages: {menu_pages}\n")
    for current_html in menu_pages:
        current_dir = os.path.dirname(current_html)
        print(f"\nFrom: {current_html}")
        for target_html in menu_pages:
            rel = os.path.relpath(target_html, start=current_dir)
            # Compute the absolute path as it would be from current_dir
            abs_link = os.path.abspath(os.path.join(current_dir, rel))
            exists = os.path.exists(abs_link)
            mark = '✓' if exists else '✗'
            debug_msg = f"  To: {target_html} => relpath: {rel} [{mark}]"
            print(debug_msg)
            logging.debug(f"From: {current_html} (dir: {current_dir}) -> To: {target_html} => relpath: {rel} [{mark}]")

if __name__ == "__main__":
    test_menu_links()
