#!/usr/bin/env python3
import yaml
import sys
from pathlib import Path
import io

repo_root = Path(__file__).parent.parent.resolve()
content_yml = repo_root / '_content.yml'
autogen_dir = repo_root / '.autogen'
autogen_dir.mkdir(parents=True, exist_ok=True)
out_files = {
    'notebooks': autogen_dir / '_notebooks.yml',
    'menu': autogen_dir / '_menu.yml',
    'config': autogen_dir / '_config.yml',
    'toc': autogen_dir / '_toc.yml',
}

def main():
    if not content_yml.exists():
        print(f"[ERROR] {content_yml} not found.")
        sys.exit(1)
    with open(content_yml, 'r') as f:
        content = yaml.safe_load(f)

    # --- Collect notebook files ---
    notebooks = []
    if 'chapters' in content:
        for chapter in content['chapters']:
            if isinstance(chapter, dict) and 'files' in chapter:
                for f in chapter['files']:
                    if 'file' in f:
                        notebooks.append(f['file'])
    if 'homework' in content:
        for hw in content['homework']:
            if 'file' in hw:
                notebooks.append(hw['file'])
    if 'activities' in content:
        for act in content['activities']:
            if 'file' in act:
                notebooks.append(act['file'])
    # Remove duplicates, preserve order
    seen = set()
    notebooks_unique = []
    for nb in notebooks:
        if nb not in seen:
            notebooks_unique.append(nb)
            seen.add(nb)

    # --- Write _notebooks.yml ---
    notebooks_comment = (
        "# AUTO-GENERATED FILE. DO NOT EDIT.\n"
        "# This file was generated from _content.yml by scripts/preprocess_content_yml.py\n"
        "# Edit _content.yml instead and re-run the preprocessor.\n"
    )
    buf = io.StringIO()
    buf.write(notebooks_comment)
    buf.write('notebooks:\n')
    for nb in notebooks_unique:
        buf.write(f'  - {nb}\n')
    with open(out_files['notebooks'], 'w') as f:
        f.write(buf.getvalue())
    print(f"[OK] Wrote {out_files['notebooks']}")

    # --- Write _toc.yml ---
    toc_comment = "# Auto-generated _toc.yml from _notebooks.yaml\n"
    toc = {
        'format': 'jb-book',
        'root': 'content/index',
        'chapters': []
    }
    for nb in notebooks_unique:
        nb_path = str(nb)
        if nb_path.endswith('.ipynb'):
            nb_path = nb_path[:-6]
        if not nb_path.startswith('content/'):
            nb_path = 'content/' + nb_path
        toc['chapters'].append({'file': nb_path})
    buf = io.StringIO()
    buf.write(toc_comment)
    yaml.dump(toc, buf, sort_keys=False, allow_unicode=True)
    with open(out_files['toc'], 'w') as f:
        f.write(buf.getvalue())
    print(f"[OK] Wrote {out_files['toc']}")

    # --- Write _menu.yml ---
    menu = []
    menu.append({'title': 'Home', 'path': 'index.html'})
    chapters_menu = {'title': 'Chapters', 'path': 'chapters.html', 'children': []}
    if 'chapters' in content:
        for chapter in content['chapters']:
            if 'files' in chapter:
                for f in chapter['files']:
                    title = f.get('title') or f.get('file')
                    path = Path(f.get('file', '')).with_suffix('.html').name if 'file' in f else ''
                    if title and path:
                        chapters_menu['children'].append({'title': title, 'path': path})
    menu.append(chapters_menu)
    activities_menu = {'title': 'Activities', 'path': 'activities.html', 'children': []}
    if 'homework' in content:
        for hw in content['homework']:
            title = hw.get('title') or hw.get('file')
            path = Path(hw.get('file', '')).with_suffix('.html').name if 'file' in hw else ''
            if title and path:
                activities_menu['children'].append({'title': title, 'path': path})
    menu.append(activities_menu)
    menu.append({'title': 'Resources', 'path': 'resources.html'})
    menu.append({'title': 'About', 'path': 'about.html'})
    menu_comment = (
        "# AUTO-GENERATED FILE. DO NOT EDIT.\n"
        "# This file was generated from _content.yml by scripts/preprocess_content_yml.py\n"
        "# Edit _content.yml instead and re-run the preprocessor.\n"
    )
    buf = io.StringIO()
    buf.write(menu_comment)
    yaml.dump({'menu': menu}, buf, sort_keys=False, allow_unicode=True)
    with open(out_files['menu'], 'w') as f:
        f.write(buf.getvalue())
    print(f"[OK] Wrote {out_files['menu']}")

    # --- Write _config.yml ---
    config = {}
    if 'site' in content:
        site = content['site']
        # Robustly handle theme: always output as dict with default/light/dark
        theme = site.get('theme', 'light')
        if isinstance(theme, str):
            theme_dict = {'default': theme, 'light': 'light', 'dark': 'dark'}
        else:
            theme_dict = theme
        config.update(site)
        config['theme'] = theme_dict
    if 'build' in content:
        config['build'] = content['build']
    config_comment = (
        "# AUTO-GENERATED FILE. DO NOT EDIT.\n"
        "# This file was generated from _content.yml by scripts/preprocess_content_yml.py\n"
        "# Edit _content.yml instead and re-run the preprocessor.\n"
    )
    with open(out_files['config'], 'w') as f:
        f.write(config_comment)
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)
    print(f"[OK] Wrote {out_files['config']}")

if __name__ == '__main__':
    main()