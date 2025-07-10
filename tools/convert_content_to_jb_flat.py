"""
convert_content_to_jb_flat.py

Script to convert _content.yml (custom menu/content tree) to a minimal, flat Jupyter Book _toc.yml.
- Only includes notebooks/files listed in toc: (recursively), in order.
- No parts, no nesting, just a flat list of files.
- The first file becomes the root.

Usage:
    python convert_content_to_jb_flat.py

Outputs:
    _toc.yml in the current directory.
"""
import yaml
from pathlib import Path

def load_content_yml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def flatten_files(menu):
    files = []
    for node in menu:
        if not isinstance(node, dict):
            continue
        file = node.get('file')
        if file:
            files.append(Path(file).with_suffix('').as_posix())
        children = node.get('children')
        if children:
            files.extend(flatten_files(children))
    return files

def write_yaml(obj, path):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(obj, f, sort_keys=False, allow_unicode=True)

def main():
    content = load_content_yml('_content.yml')
    toc_list = content.get('toc', [])
    files = flatten_files(toc_list)
    if not files:
        raise RuntimeError('No files found in toc:')
    toc = {
        'format': 'jb-book',
        'root': files[0],
        'chapters': [{'file': f} for f in files[1:]]
    }
    write_yaml(toc, '_toc.yml')
    print('[OK] Wrote flat _toc.yml with', len(files), 'files')

if __name__ == '__main__':
    main()
