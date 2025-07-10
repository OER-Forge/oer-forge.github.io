"""
menu_parser.py

Extracts the navigation menu structure from a validated _content.yml using content_parser.py.
- Only top-level items with menu: true are included as main menu entries.
- Recursively includes children for dropdowns/submenus.
- Designed for robust, testable, and debuggable menu extraction for site generators.

Usage:
    from menu_parser import get_menu_tree
    menu = get_menu_tree('_content.yml')

Debug output is printed for each menu item processed.
"""
from content_parser import load_and_validate_content_yml
from typing import List, Dict, Any, Optional

def get_menu_tree(yaml_path: str) -> List[Dict[str, Any]]:
    """
    Load and extract the menu tree from a YAML manifest.
    Returns a list of menu dicts with 'title', 'file', and optional 'children'.
    Only items with menu: true at the top level are included as main menu entries.
    """
    content = load_and_validate_content_yml(yaml_path)
    toc = content.get('toc', [])
    menu = []
    for item in toc:
        if item.get('menu', False):
            parsed = _parse_menu_item(item, level=0)
            menu.append(parsed)
    print(f"[MENU] Top-level menu: {[m['title'] for m in menu]}")
    return menu

def _parse_menu_item(item: Dict[str, Any], level: int = 0) -> Dict[str, Any]:
    """
    Recursively parse a menu item and its children for menu rendering.
    """
    debug_prefix = '  ' * level
    title = item.get('title', '<no title>')
    file = item.get('file')
    print(f"{debug_prefix}[MENU] Level {level}: {title} (file: {file})")
    menu_item = {'title': title}
    if file:
        menu_item['file'] = file
    if 'children' in item and isinstance(item['children'], list) and item['children']:
        menu_item['children'] = [_parse_menu_item(child, level=level+1) for child in item['children']]
    return menu_item
