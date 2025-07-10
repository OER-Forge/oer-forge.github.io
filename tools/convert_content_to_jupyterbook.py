"""
convert_content_to_jupyterbook.py

Script to convert _content.yml (custom menu/content tree) to Jupyter Book _config.yml and _toc.yml.
- _config.yml: minimal, with title, logo, description, and language.
- _toc.yml: Jupyter Book Table of Contents, with flat or nested structure matching _content.yml.

Usage:
    python convert_content_to_jupyterbook.py

Outputs:
    _config.yml and _toc.yml in the current directory.
"""
import yaml
import sys
from pathlib import Path

def slugify(title):
    import re
    slug = title.lower().strip()
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    return slug

def load_content_yml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def make_config_yml(site):
    config = {
        'title': site.get('title', 'Jupyter Book'),
        'logo': site.get('logo', ''),
        'description': site.get('description', ''),
        'language': site.get('language', 'en'),
    }
    return config

def make_toc_entries(menu):
    """
    Recursively convert menu tree to Jupyter Book toc entries.
    Each entry: {'file': path, 'title': ...} or {'part': ..., 'sections': [...]}
    """
    entries = []
    for node in menu:
        if not isinstance(node, dict):
            continue
        title = node.get('title', '')
        file = node.get('file')
        children = node.get('children')
        if file:
            # Remove extension for Jupyter Book (expects .md/.ipynb omitted)
            file_path = Path(file)
            stem = file_path.with_suffix('').as_posix()
            entry = {'file': stem, 'title': title}
            if children:
                child_chapters = make_toc_entries(children)
                if child_chapters:
                    entry['chapters'] = child_chapters
            entries.append(entry)
        elif children:
            # Only use 'part' for non-root levels; flatten at root
            child_chapters = make_toc_entries(children)
            if child_chapters:
                # If this is the root level, flatten children
                if title.lower() == 'chapters' or title.lower() == 'sections':
                    entries.extend(child_chapters)
                else:
                    entry = {'part': title, 'chapters': child_chapters}
                    entries.append(entry)
    return entries
    return entries

def write_yaml(obj, path):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(obj, f, sort_keys=False, allow_unicode=True)

def main():
    content = load_content_yml('_content.yml')
    site = content.get('site', {})
    toc_list = content.get('toc', [])
    # _config.yml
    config = make_config_yml(site)
    write_yaml(config, '_config.yml')
    print('[OK] Wrote _config.yml')
    # Find root file (first file in top-level toc)
    def find_first_file_and_rest(toc):
        for i, node in enumerate(toc):
            if node.get('file'):
                root_file = Path(node['file']).with_suffix('').as_posix()
                # All other nodes after the first file node
                rest = toc[:i] + toc[i+1:]
                return root_file, rest
        return 'index', toc

    root_file, rest = find_first_file_and_rest(toc_list)
    # Find the title for the root file
    def get_root_title(toc, root_file):
        for node in toc:
            if node.get('file'):
                return node.get('title', 'Home')
        return 'Home'
    root_title = get_root_title(toc_list, root_file)


    # All other top-level nodes (except the root) become chapters/parts under the root
    def make_chapters(rest):
        chapters = []
        for node in rest:
            if not isinstance(node, dict):
                continue
            file = node.get('file')
            title = node.get('title', '')
            children = node.get('children')
            if file:
                entry = {'file': Path(file).with_suffix('').as_posix(), 'title': title}
                if children:
                    entry['chapters'] = make_toc_entries(children)
                chapters.append(entry)
            elif children:
                # If this is a top-level grouping (e.g., 'Chapters'), flatten its children
                if title.lower() in ('chapters', 'sections'):
                    chapters.extend(make_toc_entries(children))
                else:
                    chapters.append({'part': title, 'chapters': make_toc_entries(children)})
        return chapters

    toc = {
        'format': 'jb-book',
        'root': root_file,
        'chapters': make_chapters(rest)
    }
    write_yaml(toc, '_toc.yml')
    print('[OK] Wrote _toc.yml')

if __name__ == '__main__':
    main()
