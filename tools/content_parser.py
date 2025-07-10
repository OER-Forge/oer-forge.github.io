
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
import glob
import os

class ContentValidationError(Exception):
    pass

def load_and_validate_content_yml(path: str) -> dict:
    """
    Load and validate the _content.yml file. Raises ContentValidationError on error.
    """
    with open(path, 'r') as f:
        content = yaml.safe_load(f)
    validate_content(content)
    # Expand .autogen and append_children in toc if present
    if 'toc' in content:
        base_path = os.path.dirname(os.path.abspath(path))
        content['toc'] = _process_special_keys(content['toc'], base_path)
    return content


# --- .autogen and append_children support ---
def _expand_autogen(entry, base_path):
    """Expand an entry with a .autogen key into a list of file entries."""
    pattern = entry[".autogen"]
    # Use glob relative to base_path
    files = sorted(glob.glob(os.path.join(base_path, pattern)))
    return [{"file": os.path.relpath(f, base_path)} for f in files]

def _append_children(entry, base_path):
    """Append children from a directory to the entry."""
    dir_path = os.path.join(base_path, entry["append_children"])
    files = sorted([f for f in glob.glob(os.path.join(dir_path, "*")) if os.path.isfile(f)])
    children = [{"file": os.path.relpath(f, base_path)} for f in files]
    if "children" in entry:
        entry["children"].extend(children)
    else:
        entry["children"] = children
    return entry

def _process_special_keys(entries, base_path):
    result = []
    for entry in entries:
        if ".autogen" in entry:
            result.extend(_expand_autogen(entry, base_path))
        elif "append_children" in entry:
            result.append(_append_children(entry, base_path))
        else:
            # Recursively process children
            if "children" in entry:
                entry["children"] = _process_special_keys(entry["children"], base_path)
            result.append(entry)
    return result

def validate_content(content: dict):
    # Validate 'site' section
    if 'site' not in content or not isinstance(content['site'], dict):
        raise ContentValidationError("Missing or invalid 'site' (must be a dict) in _content.yml.")
    required_site_keys = [
        'title', 'author', 'description', 'logo', 'favicon', 'theme', 'language', 'github_url'
    ]
    for key in required_site_keys:
        if key not in content['site']:
            raise ContentValidationError(f"Missing required key in 'site': {key}")
    if not isinstance(content['site']['theme'], dict):
        raise ContentValidationError("'theme' in 'site' must be a dict")
    for theme_key in ['default', 'light', 'dark']:
        if theme_key not in content['site']['theme']:
            raise ContentValidationError(f"Missing theme key in 'site.theme': {theme_key}")

    # Validate 'toc' section
    if 'toc' not in content or not isinstance(content['toc'], list):
        raise ContentValidationError("Missing or invalid 'toc' (must be a list) in _content.yml.")
    for item in content['toc']:
        validate_menu_item(item, level=0)


    # Validate 'footer' section
    if 'footer' not in content or not isinstance(content['footer'], dict):
        raise ContentValidationError("Missing or invalid 'footer' (must be a dict) in _content.yml.")
    if 'text' not in content['footer'] or not isinstance(content['footer']['text'], str):
        raise ContentValidationError("Missing or invalid 'text' in 'footer' section of _content.yml.")

    # Validate 'static' section
    if 'static' not in content or not isinstance(content['static'], dict):
        raise ContentValidationError("Missing or invalid 'static' (must be a dict) in _content.yml.")
    static_keys = ['images', 'css', 'js', 'templates', 'themes']
    for key in static_keys:
        if key not in content['static']:
            raise ContentValidationError(f"Missing required key in 'static': {key}")
        if not isinstance(content['static'][key], list):
            raise ContentValidationError(f"'{key}' in 'static' must be a list")
        for entry in content['static'][key]:
            if not isinstance(entry, dict):
                raise ContentValidationError(f"Each entry in 'static.{key}' must be a dict")
            if 'path' not in entry or 'description' not in entry:
                raise ContentValidationError(f"Each entry in 'static.{key}' must have 'path' and 'description'")
            if not isinstance(entry['path'], str) or not isinstance(entry['description'], str):
                raise ContentValidationError(f"'path' and 'description' in 'static.{key}' must be strings")

    # Validate 'build' section
    if 'build' not in content or not isinstance(content['build'], dict):
        raise ContentValidationError("Missing or invalid 'build' (must be a dict) in _content.yml.")
    required_build_keys = [
        'outputs', 'output_dir', 'docs_dir', 'sources_dir', 'notebooks_dir', 'static_dir', 'images_dir'
    ]
    for key in required_build_keys:
        if key not in content['build']:
            raise ContentValidationError(f"Missing required key in 'build': {key}")
    if not isinstance(content['build']['outputs'], list) or not all(isinstance(x, str) for x in content['build']['outputs']):
        raise ContentValidationError("'outputs' in 'build' must be a list of strings")
    for key in required_build_keys[1:]:
        if not isinstance(content['build'][key], str):
            raise ContentValidationError(f"'{key}' in 'build' must be a string")

def validate_menu_item(item: dict, level: int):
    # Enforce max depth (menu > group > subgroup > page):
    print(f"[DEBUG] validate_menu_item: level={level}, title={item.get('title')}, keys={list(item.keys())}")
    if level > 3:
        print(f"[DEBUG] Exceeded max depth at level {level} for item: {item}")
        raise ContentValidationError(f"Exceeded max depth (menu > group > subgroup > page) at level {level}: {item}")
    if not isinstance(item, dict):
        print(f"[DEBUG] Not a dict at level {level}: {item}")
        raise ContentValidationError(f"Menu/group/page item at level {level} is not a dict: {item}")
    if 'title' not in item or not isinstance(item['title'], str):
        print(f"[DEBUG] Missing or invalid 'title' at level {level}: {item}")
        raise ContentValidationError(f"Missing or invalid 'title' at level {level}: {item}")
    if 'menu' in item and not isinstance(item['menu'], bool):
        print(f"[DEBUG] 'menu' not bool at level {level}: {item}")
        raise ContentValidationError(f"'menu' must be boolean at level {level}: {item}")
    if 'file' in item and not isinstance(item['file'], str):
        print(f"[DEBUG] 'file' not string at level {level}: {item}")
        raise ContentValidationError(f"'file' must be a string at level {level}: {item}")
    if 'children' in item:
        if not isinstance(item['children'], list):
            print(f"[DEBUG] 'children' not list at level {level}: {item}")
            raise ContentValidationError(f"'children' must be a list at level {level}: {item}")
        for child in item['children']:
            validate_menu_item(child, level=level+1)
        # After children, return early to avoid further checks
        return
    # Leaf node must have a file
    if 'file' not in item:
        print(f"[DEBUG] Leaf node missing 'file' at level {level}: {item}")
        raise ContentValidationError(f"Leaf node missing 'file' at level {level}: {item}")

def get_menu_structure(content: dict) -> List[dict]:
    """
    Return the list of top-level menu items (those with menu: true).
    """
    return [item for item in content['toc'] if item.get('menu', False)]

def get_all_content_files(content: dict) -> List[str]:
    """
    Recursively collect all 'file' values from the toc tree.
    """
    files = []
    def walk(node):
        if 'file' in node:
            files.append(node['file'])
        if 'children' in node:
            for child in node['children']:
                walk(child)
    for item in content['toc']:
        walk(item)
    return files

def get_group_page_info(content: dict, group_title: str) -> Optional[dict]:
    """
    Find a group by title and return its dict (with file, children, etc), or None if not found.
    """
    def walk(node):
        if node.get('title', '').lower() == group_title.lower():
            return node
        if 'children' in node:
            for child in node['children']:
                found = walk(child)
                if found:
                    return found
        return None
    for item in content['toc']:
        found = walk(item)
        if found:
            return found
    return None
