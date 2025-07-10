def build_tex_all(debug=False):
    """Build LaTeX for all files referenced in the menu/content tree (_content.yml)."""
    from content_parser import load_and_validate_content_yml, get_all_content_files
    content = load_and_validate_content_yml('_content.yml')
    files = get_all_content_files(content)
    if not files:
        if debug:
            print("[WARN] No files found in _content.yml toc.")
        return
    if debug:
        print(f"[INFO] Building LaTeX for {len(files)} files from menu/content tree.")
    build_tex_for_files(files, debug=debug)

def build_tex_for_files(files, debug=False):
    """Build LaTeX for specified markdown and notebook files."""
    import subprocess
    import sys
    import os
    from pathlib import Path
    import shutil
    import re
    repo_root = Path(__file__).parent.resolve()
    tex_dir = repo_root / 'docs' / 'tex'
    img_dir = repo_root / 'docs' / 'images'
    tex_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)
    missing_files = []
    for file in files:
        file_path = Path(file)
        if not file_path.exists():
            print(f"[ERROR] File not found: {file}")
            missing_files.append(file)
            continue
        ext = file_path.suffix.lower()
        stem = file_path.stem
        out_md = tex_dir / f"{stem}.md"
        out_tex = tex_dir / f"{stem}.tex"
        # Step 1: Ensure we have a markdown file with correct image links
        if ext == '.md':
            print(f"[INFO] Copying markdown file: {file_path} -> {out_md}")
            shutil.copy2(file_path, out_md)
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            def replace_img_link(match):
                img_path = match.group(1)
                if img_path.startswith('http'):
                    return match.group(0)
                img_filename = os.path.basename(img_path)
                flat_name = f"{stem}_{img_filename}"
                src_img = file_path.parent / img_path
                dest_img = img_dir / flat_name
                if src_img.exists():
                    shutil.copy2(src_img, dest_img)
                    print(f"[INFO] Copied image {src_img} -> {dest_img}")
                # For tex, use relative path from tex_dir to img_dir
                rel_path = os.path.relpath(dest_img, tex_dir)
                return match.group(0).replace(img_path, rel_path)
            new_md_content = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', replace_img_link, md_content)
            with open(out_md, 'w', encoding='utf-8') as f:
                f.write(new_md_content)
        elif ext == '.ipynb':
            print(f"[INFO] Converting notebook to markdown: {file_path} -> {out_md}")
            import nbformat
            import subprocess
            nb = nbformat.read(str(file_path), as_version=4)
            tmp_md = tex_dir / f"{stem}_tmp.md"
            cmd = [sys.executable, '-m', 'nbconvert', '--to', 'markdown', str(file_path), '--output', tmp_md.name, '--output-dir', str(tex_dir)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[ERROR] nbconvert failed for {file_path}: {result.stderr}")
                continue
            with open(tmp_md, 'r', encoding='utf-8') as f:
                md_content = f.read()
            def replace_img_link(match):
                img_path = match.group(1)
                if img_path.startswith('http'):
                    return match.group(0)
                img_filename = os.path.basename(img_path)
                flat_name = f"{stem}_{img_filename}"
                src_img = tex_dir / img_path
                dest_img = img_dir / flat_name
                if src_img.exists():
                    shutil.copy2(src_img, dest_img)
                    print(f"[INFO] Copied image {src_img} -> {dest_img}")
                rel_path = os.path.relpath(dest_img, tex_dir)
                return match.group(0).replace(img_path, rel_path)
            new_md_content = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', replace_img_link, md_content)
            with open(out_md, 'w', encoding='utf-8') as f:
                f.write(new_md_content)
            tmp_md.unlink()
        else:
            print(f"[SKIP] Unsupported file type: {file}")
            continue
        # Step 2: Convert markdown to tex with pandoc
        print(f"[INFO] Converting markdown to tex: {out_md} -> {out_tex}")
        cmd = ['pandoc', str(out_md), '-o', str(out_tex), '--resource-path', str(img_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] pandoc failed for {out_md}: {result.stderr}")
            continue
        print(f"[OK] Built {out_tex} from {file}")
    if missing_files:
        print(f"[SUMMARY] {len(missing_files)} file(s) were missing and not processed:")
        for mf in missing_files:
            print(f"  - {mf}")
def render_download_buttons(file_path):
    """
    Generate HTML for download buttons for a given file (md or ipynb).
    Uses .download-btn CSS. Follows the pattern from the live site.
    For .ipynb files, dynamically finds the correct Jupyter Book HTML path.
    """
    import os
    from pathlib import Path
    stem = os.path.splitext(os.path.basename(file_path))[0]
    ext = os.path.splitext(file_path)[1].lower()
    # Always show these
    buttons = [
        (f'pdf/{stem}.pdf', 'PDF', '📄', True),
        (f'md/{stem}.md', 'MD', '✍️', True),
        (f'docx/{stem}.docx', 'DOCX', '📝', True),
        (f'tex/{stem}.tex', 'TEX', '📐', True),
    ]
    # Add ipynb and jupyter for notebooks
    if ext == '.ipynb':
        buttons.append((f'ipynb/{stem}.ipynb', 'IPYNB', '📓', True))
        # Dynamically find the Jupyter Book HTML file
        jupyter_html = None
        jupyter_root = Path('docs/jupyter-book/content/notebooks')
        if jupyter_root.exists():
            for html_file in jupyter_root.rglob(f'{stem}.html'):
                # Use the first match found
                rel_path = html_file.relative_to('docs')
                jupyter_html = str(rel_path)
                break
        if jupyter_html:
            buttons.append((jupyter_html, 'Jupyter', '🔗', False))
        else:
            # Fallback: keep the old (likely broken) path, but mark as disabled
            buttons.append((f'jupyter/content/notebooks/{stem}.html', 'Jupyter (not found)', '❌', False))
    html = ['<nav class="chapter-downloads" aria-label="Download chapter sources">']
    html.append('<div role="group" aria-label="Download formats">')
    for href, label, icon, is_download in buttons:
        attrs = f'class="download-btn" href="{href}"'
        if is_download:
            attrs += ' download'
        if label.startswith('Jupyter'):
            attrs += ' target="_blank" rel="noopener"'
        if 'not found' in label:
            attrs += ' style="pointer-events:none;opacity:0.5;"'
        html.append(f'<a {attrs}><span aria-hidden="true">{icon}</span> {label}</a>')
    html.append('</div></nav>')
    return '\n'.join(html)


import shutil

def copy_static_assets(debug=False):
    """Copy CSS and image assets from static/ to docs/."""
    # Copy CSS
    css_src = Path('static/css')
    css_dest = Path('docs/css')
    if css_src.exists():
        css_dest.mkdir(parents=True, exist_ok=True)
        for css_file in css_src.glob('*.css'):
            dest = css_dest / css_file.name
            shutil.copy2(css_file, dest)
            debug_print(f"[INFO] Copied {css_file} to {dest}", debug)
    else:
        debug_print(f"[WARN] Source CSS directory {css_src} does not exist.", debug)
    # Copy images
    img_src = Path('static/images')
    img_dest = Path('docs/images')
    if img_src.exists():
        img_dest.mkdir(parents=True, exist_ok=True)
        for img_file in img_src.glob('*'):
            if img_file.is_file():
                dest = img_dest / img_file.name
                shutil.copy2(img_file, dest)
                debug_print(f"[INFO] Copied {img_file} to {dest}", debug)
    else:
        debug_print(f"[WARN] Source images directory {img_src} does not exist.", debug)
def debug_print(msg, debug):
    if debug:
        print(msg)
#!/usr/bin/env python3

"""
build-html.py

Skeleton script for building site outputs with flexible CLI flags.
Supports: --html, --md, --docx, --tex, --pdf, --jupyter, --ppt, and --files FILE1 FILE2 ...

No build logic yet—just argument parsing and structure.
"""

import argparse
import sys
import subprocess


# --- Move build_html_all and build_html_for_files above main() ---


def build_html_all(debug=False):
    copy_static_assets(debug=debug)
    """Build HTML for all files referenced in the menu/content tree (_content.yml)."""
    from content_parser import load_and_validate_content_yml, get_all_content_files
    content = load_and_validate_content_yml('_content.yml')
    files = get_all_content_files(content)
    if not files:
        if debug:
            print("[WARN] No files found in _content.yml toc.")
        return
    if debug:
        print(f"[INFO] Building HTML for {len(files)} files from menu/content tree.")
    build_html_for_files(files, debug=debug)

from pathlib import Path
import os
import sys
try:
    import markdown
except ImportError:
    print("[ERROR] The 'markdown' package is required. Install with: pip install markdown", file=sys.stderr)
    sys.exit(1)
from content_parser import load_and_validate_content_yml
from build_menu_html import build_menu_ul
from build_footer_html import render_footer
from menu_parser import get_menu_tree

from notebook_kernel_utils import fix_all_notebook_kernels

def build_html_for_files(files, debug=False):
    # Always fix kernels before building
    fix_all_notebook_kernels("content/", debug=debug)
    debug_print("[DEBUG] build_html_for_files() is running!", debug)
    """
    Build HTML for specified markdown and notebook files using YAML-driven templates and navigation.
    debug: if True, print debug output for menu and notebook processing.
    """
    # Load site config and menu
    content = load_and_validate_content_yml('_content.yml')
    site = content['site']
    try:
        menu = get_menu_tree('_content.yml')
        if isinstance(menu, dict) and 'toc' in menu:
            menu = menu['toc']
    except Exception as e:
        print(f"[ERROR] Could not load menu: {e}")
        menu = []


    import re
    def slugify(title):
        # Lowercase, replace spaces with hyphens, remove non-alphanum except hyphens
        slug = title.lower().strip()
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        return slug

    def file_to_html_link(file_path, title, is_auto_index=False):
        if is_auto_index:
            base = slugify(title)
        else:
            base, ext = os.path.splitext(os.path.basename(file_path))
        return f'<a href="{base}.html">{title}</a>'

    def first_child_file(node):
        if 'children' in node:
            for child in node['children']:
                if isinstance(child, dict):
                    if 'file' in child:
                        return child['file']
                    result = first_child_file(child)
                    if result:
                        return result
        return None

    def top_level_menu_items(menu):
        items = []
        if isinstance(menu, list):
            for node in menu:
                if not isinstance(node, dict):
                    continue
                title = node.get('title')
                file = node.get('file')
                is_auto_index = False
                if not file and node.get('children'):
                    # This is an auto-generated index
                    is_auto_index = True
                    file = slugify(title) + '.html'
                elif file:
                    # Use the file as normal
                    pass
                if title and (file or node.get('children')):
                    items.append((file, title, node, is_auto_index))
        return items

    top_menu = top_level_menu_items(menu)

    menu_html = ['<ul class="site-nav-menu" id="site-nav-menu">']
    for file, title, _, is_auto_index in top_menu:
        menu_html.append('<li>')
        menu_html.append(file_to_html_link(file, title, is_auto_index=is_auto_index))
        menu_html.append('</li>')
    menu_html.append('</ul>')
    menu_html = ''.join(menu_html)

    footer_text = content.get('footer', {}).get('text', '')
    # Load footer from template and fill variable
    with open('static/templates/footer.html', 'r', encoding='utf-8') as f:
        footer_html = f.read().replace('{{ footer_text }}', footer_text)

    # Load header HTML from template and fill variables
    logo = site['logo']
    title = site['title']
    description = site.get('description', '')
    logo_web = './' + logo[len('static/'):] if logo.startswith('static/') else logo
    with open('static/templates/header.html', 'r', encoding='utf-8') as f:
        header_html = f.read()
    header_html = (header_html
        .replace('{{ logo_web }}', logo_web)
        .replace('{{ title }}', title)
        .replace('{{ description }}', description)
    )

    # Load theme toggle HTML from template
    with open('static/templates/theme-toggle.html', 'r', encoding='utf-8') as f:
        theme_toggle_html = f.read()

    head_path = os.path.join('static', 'templates', 'head.html')
    with open(head_path, 'r') as f:
        head_template = f.read()
    css_light = 'css/theme-light.css'
    css_dark = 'css/theme-dark.css'

    import nbformat
    import base64
    debug_print(f"[DEBUG] build_html_for_files called with {len(files)} files:", debug)
    for f in files:
        debug_print(f"  - {f}", debug)
    debug_print(f"[DEBUG] Current working directory: {os.getcwd()}", debug)
    debug_print(f"[DEBUG] Output directory absolute path: {str(Path('docs').resolve())}", debug)
    debug_print(f"[DEBUG] Output directory exists: {Path('docs').exists()}", debug)
    debug_print("[DEBUG] Listing files in output directory (docs/):", debug)
    try:
        for p in Path('docs').iterdir():
            debug_print(f"    - {p.name} (dir: {p.is_dir()}, file: {p.is_file()})", debug)
            if p.is_dir():
                for subp in p.iterdir():
                    debug_print(f"      - {subp.name} (dir: {subp.is_dir()}, file: {subp.is_file()})", debug)
    except Exception as e:
        debug_print(f"[ERROR] Could not list docs/: {e}", debug)
    debug_print("[DEBUG] Starting main file processing loop...", debug)
    missing_files = []

    # --- Auto-generate index pages for top-level menus with no file ---
    for file, title, node, is_auto_index in top_menu:
        if is_auto_index:
            # Always generate at slugified-title.html for auto-indexes
            slug = slugify(title)
            out_path = Path('docs') / f"{slug}.html"
            # Build a list of children (and grandchildren)
            def render_children(children, level=1):
                html = []
                for child in children:
                    if not isinstance(child, dict):
                        continue
                    child_title = child.get('title', '(untitled)')
                    child_file = child.get('file')
                    child_children = child.get('children')
                    # Use h2/h3/h4 for subgroups, and always list grandchildren if present
                    if child_file and child_children:
                        # Submenu/group with a file: link and heading, then list grandchildren
                        heading_tag = f'h{min(level+1, 4)}'
                        html.append(f'<{heading_tag}>{file_to_html_link(child_file, child_title)}</{heading_tag}>')
                        html.append(render_children(child_children, level+1))
                    elif child_file:
                        # Just a file
                        html.append(f'<li>{file_to_html_link(child_file, child_title)}</li>')
                    elif child_children:
                        # Submenu/group with no file: heading, then list grandchildren
                        heading_tag = f'h{min(level+1, 4)}'
                        html.append(f'<{heading_tag}>{child_title}</{heading_tag}>')
                        html.append(render_children(child_children, level+1))
                # Only wrap in <ul> if there are <li> children at this level
                if any(x.startswith('<li>') for x in html):
                    return '<ul class="menu-section">' + ''.join(html) + '</ul>'
                else:
                    return ''.join(html)
            section_html = f'<h2>{title}</h2>'
            if node.get('description'):
                section_html += f'<div class="menu-description">{node["description"]}</div>'
            section_html += render_children(node['children'])
            page_title = title
            head_html = head_template.replace('{{ title }}', page_title).replace('{{ css_light }}', css_light).replace('{{ css_dark }}', css_dark)
            full_html = f'''<!DOCTYPE html>\n<html lang="{site.get('language', 'en')}">\n{head_html}\n<body>\n  {header_html}\n  <nav class="site-nav" id="site-nav" aria-label="Main navigation">{menu_html}</nav>\n  <main class="site-main container">\n    {theme_toggle_html}\n    {section_html}\n  </main>\n  <footer>\n    {footer_html}\n  </footer>\n</body>\n</html>\n'''
            out_path.parent.mkdir(exist_ok=True)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            debug_print(f"[OK] Auto-generated index page: {out_path}", debug)

    # --- Normal file build logic ---
    for file in files:
        debug_print(f"[DEBUG] ---\n[DEBUG] Processing file: {file}", debug)
        file_path = Path(file)
        debug_print(f"[DEBUG] Starting processing for: {file}", debug)
        if not file_path.exists():
            debug_print(f"[ERROR] File not found: {file}", debug)
            missing_files.append(file)
            continue
        ext = file_path.suffix.lower()
        debug_print(f"[DEBUG] File extension: {ext}", debug)
        try:
            download_html = render_download_buttons(str(file_path))
            if ext == '.md':
                debug_print(f"[DEBUG] Reading markdown file: {file_path}", debug)
                with open(file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                debug_print(f"[DEBUG] Rendering markdown to HTML...", debug)
                body_html = markdown.markdown(md_content, extensions=['extra', 'toc', 'tables'])
            elif ext == '.ipynb':
                debug_print(f"[DEBUG] Reading notebook file: {file_path}", debug)
                try:
                    nb = nbformat.read(str(file_path), as_version=4)
                except Exception as e:
                    debug_print(f"[ERROR] Could not read notebook: {file_path}: {e}", debug)
                    continue
                debug_print(f"[DEBUG] Notebook loaded. Keys: {list(nb.keys())}", debug)
                if not nb.get('cells'):
                    debug_print(f"[WARN] Notebook {file_path} has no cells.", debug)
                    continue
                debug_print(f"[DEBUG] Notebook {file_path} has {len(nb['cells'])} cells.", debug)
                body_html = []
                for idx, cell in enumerate(nb.get('cells', [])):
                    debug_print(f"[DEBUG] Processing cell {idx+1} of type {cell.get('cell_type')}", debug)
                    cell_type = cell.get('cell_type')
                    lang = cell.get('metadata', {}).get('language', 'python' if cell_type == 'code' else 'markdown')
                    debug_print(f"[DEBUG] Cell {idx}: type={cell_type}, lang={lang}", debug)
                    if cell_type == 'markdown':
                        import markdown as mdmod
                        try:
                            debug_print(f"[DEBUG] Rendering markdown cell {idx+1}", debug)
                            cell_html = mdmod.markdown(''.join(cell.get('source', [])), extensions=['extra', 'toc', 'tables'])
                            body_html.append(f'<div class="notebook-markdown-cell">{cell_html}</div>')
                        except Exception as e:
                            debug_print(f"[ERROR] Failed to render markdown cell {idx+1} in {file_path}: {e}", debug)
                    elif cell_type == 'code':
                        debug_print(f"[DEBUG] Rendering code cell {idx+1}", debug)
                        code = ''.join(cell.get('source', []))
                        code_html = f'<pre class="notebook-code-cell"><code>{code}</code></pre>'
                        outputs_html = []
                        for oidx, output in enumerate(cell.get('outputs', [])):
                            otype = output.get('output_type')
                            debug_print(f"[DEBUG]   Output {oidx+1}: type={otype}", debug)
                            try:
                                if otype == 'stream':
                                    text = ''.join(output.get('text', []))
                                    outputs_html.append(f'<div class="notebook-output-stream">{text}</div>')
                                elif otype == 'execute_result' or otype == 'display_data':
                                    data = output.get('data', {})
                                    if 'text/plain' in data:
                                        outputs_html.append(f'<div class="notebook-output-text">{data["text/plain"]}</div>')
                                    if 'image/png' in data:
                                        img_data = data['image/png']
                                        outputs_html.append(f'<img class="notebook-output-img" src="data:image/png;base64,{img_data}" />')
                                    if 'image/jpeg' in data:
                                        img_data = data['image/jpeg']
                                        outputs_html.append(f'<img class="notebook-output-img" src="data:image/jpeg;base64,{img_data}" />')
                                    if 'text/html' in data:
                                        outputs_html.append(f'<div class="notebook-output-html">{data["text/html"]}</div>')
                                elif otype == 'error':
                                    ename = output.get('ename', '')
                                    evalue = output.get('evalue', '')
                                    traceback = output.get('traceback', [])
                                    tb_html = '<br>'.join(traceback)
                                    outputs_html.append(f'<div class="notebook-output-error"><b>{ename}: {evalue}</b><br>{tb_html}</div>')
                            except Exception as e:
                                debug_print(f"[ERROR] Failed to render output {oidx+1} in code cell {idx+1} in {file_path}: {e}", debug)
                        cell_block = code_html + ''.join(outputs_html)
                        body_html.append(f'<div class="notebook-code-cell-block">{cell_block}</div>')
                body_html = '\n'.join(body_html)
            else:
                debug_print(f"[SKIP] Unsupported file type: {file}", debug)
                continue
            if not body_html:
                debug_print(f"[WARN] No content generated for {file_path}, skipping HTML output.", debug)
                continue
            page_title = title
            head_html = head_template.replace('{{ title }}', page_title).replace('{{ css_light }}', css_light).replace('{{ css_dark }}', css_dark)
            # Use page skeleton template
            with open('static/templates/page.html', 'r', encoding='utf-8') as f:
                page_template = f.read()
            full_html = page_template \
                .replace('{{ language }}', site.get('language', 'en')) \
                .replace('{{ head_html }}', head_html) \
                .replace('{{ header_html }}', header_html) \
                .replace('{{ menu_html }}', menu_html) \
                .replace('{{ theme_toggle_html }}', theme_toggle_html) \
                .replace('{{ download_html }}', download_html) \
                .replace('{{ body_html }}', body_html) \
                .replace('{{ footer_html }}', footer_html)
            out_dir = Path('docs')
            out_dir.mkdir(exist_ok=True)
            out_name = file_path.stem + '.html'
            out_path = out_dir / out_name
            try:
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                debug_print(f"[OK] Built {out_path} from {file}", debug)
            except Exception as e:
                debug_print(f"[ERROR] Failed to write HTML file {out_path}: {e}", debug)
        except Exception as e:
            debug_print(f"[FATAL] Unexpected error processing {file}: {e}", debug)
    if missing_files:
        debug_print(f"[SUMMARY] {len(missing_files)} file(s) were missing and not processed:", debug)
        for mf in missing_files:
            debug_print(f"  - {mf}", debug)
        # Always output a valid HTML page with .container for any fallback or summary
        # (This block is only for summary, not for outputting a page, so no fallback HTML is written here)

import subprocess
def build_jupyter_for_files(debug=False):
    """
    Orchestrate a robust Jupyter Book build:
    1. Generate flat _toc.yml
    2. Fix notebook kernels
    3. Validate TOC and kernels
    4. Build Jupyter Book
    """
    def run_script(cmd, desc):
        import subprocess
        print(f"[JUPYTER BUILD] {desc}...\n  $ {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] {desc} failed:\n{result.stderr}")
            raise RuntimeError(f"Step failed: {desc}")
        if debug:
            print(result.stdout)
    # 1. Generate flat _toc.yml
    run_script([sys.executable, 'convert_content_to_jb_flat.py'], 'Generate flat _toc.yml')
    # 2. Fix notebook kernels
    run_script([sys.executable, 'fix_notebook_kernels.py'], 'Fix notebook kernels')
    # 2.5. Ensure the Jupyter kernel is registered (idempotent)
    import sys as _sys
    def ensure_kernel():
        try:
            import ipykernel
            import jupyter_client.kernelspec
            ksm = jupyter_client.kernelspec.KernelSpecManager()
            if 'open-physics-ed' in ksm.find_kernel_specs():
                print('[OK] Jupyter kernel "open-physics-ed" already registered.')
                return
            print('[INFO] Registering Jupyter kernel: open-physics-ed')
            import subprocess
            result = subprocess.run([
                _sys.executable, '-m', 'ipykernel', 'install', '--user', '--name', 'open-physics-ed', '--display-name', 'Python (open-physics-ed)'
            ], capture_output=True, text=True)
            if result.returncode == 0:
                print('[OK] Registered Jupyter kernel: open-physics-ed')
            else:
                print('[ERROR] Failed to register kernel:')
                print(result.stderr)
        except Exception as e:
            print(f'[ERROR] Could not ensure Jupyter kernel: {e}')
    ensure_kernel()
    # 3. Validate TOC and kernels
    run_script([sys.executable, 'validate_yaml.py', '_toc.yml'], 'Validate _toc.yml YAML')
    run_script([sys.executable, 'validate_jb_toc.py', '_toc.yml'], 'Validate _toc.yml for duplicates')
    run_script([sys.executable, 'check_notebook_kernels.py', '--debug'], 'Check notebook kernels')
    # 4. Build Jupyter Book
    # Run jupyter-book build . and stream output live for better feedback
    print('[JUPYTER BUILD] Jupyter Book build (jupyter-book build .)...\n  $ jupyter-book build .')
    import subprocess
    proc = subprocess.Popen(
        ['jupyter-book', 'build', '.'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        print(line, end='')
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError('Step failed: Jupyter Book build (jupyter-book build .)')
        # Copy Jupyter Book HTML output to docs/jupyter-book/
    src = '_build/html'
    dest = 'docs/jupyter-book'
    if os.path.exists(src):
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print(f'[JUPYTER BUILD] Copied Jupyter Book HTML from {src} to {dest}')
    else:
        print(f'[JUPYTER BUILD] WARNING: Source directory {src} does not exist. No files copied.')

def main():
    parser = argparse.ArgumentParser(description="Build site outputs from content.")
    parser.add_argument('--all', action='store_true', help='Build all outputs in sequence (md, docx, tex, pdf, jupyter, ipynb, html)')
    parser.add_argument('--html', action='store_true', help='Build HTML output')
    parser.add_argument('--ipynb', action='store_true', help='Copy Jupyter notebooks to flat _build/ipynb and docs/ipynb')
    parser.add_argument('--md', action='store_true', help='Build Markdown output')
    parser.add_argument('--docx', action='store_true', help='Build DOCX output')
    parser.add_argument('--tex', action='store_true', help='Build LaTeX output')
    parser.add_argument('--pdf', action='store_true', help='Build PDF output')
    parser.add_argument('--jupyter', action='store_true', help='Build Jupyter Notebook output')
    parser.add_argument('--ppt', action='store_true', help='Build PowerPoint output')
    parser.add_argument('--files', nargs='+', help='Only build the specified files')
    parser.add_argument('--debug', action='store_true', help='Print debug information about menu extraction')
    args = parser.parse_args()


    # All build
    if args.all:
        if args.debug:
            print("[INFO] Full build (--all) selected.")
        build_md_all(debug=args.debug)
        build_docx_all(debug=args.debug)
        build_tex_all(debug=args.debug)
        build_pdf_all(debug=args.debug)
        build_jupyter_for_files(debug=args.debug)
        # IPYNB flat copy build
        cmd = [sys.executable, 'copy_ipynb_flat.py']
        if args.debug:
            cmd.append('--debug')
        print(f"[INFO] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"[ERROR] copy_ipynb_flat.py failed with exit code {result.returncode}")
            sys.exit(result.returncode)
        build_html_all(debug=args.debug)
        return
    # LaTeX build
    if args.tex:
        if args.debug:
            print("[INFO] LaTeX build selected.")
        if args.files:
            if args.debug:
                print(f"[INFO] Building LaTeX for specified files: {args.files}")
            build_tex_for_files(args.files, debug=args.debug)
        else:
            if args.debug:
                print("[INFO] Building LaTeX for all content.")
            build_tex_all(debug=args.debug)

    if args.debug:
        print("[INFO] Build flags:")
        print(f"  HTML:    {args.html}")
        print(f"  Markdown:{args.md}")
        print(f"  DOCX:    {args.docx}")
        print(f"  LaTeX:   {args.tex}")
        print(f"  PDF:     {args.pdf}")
        print(f"  Jupyter: {args.jupyter}")
        print(f"  PPT:     {args.ppt}")
        print(f"  Files:   {args.files}")

    # Jupyter Book build
    if args.jupyter:
        if args.debug:
            print("[INFO] Jupyter Book build selected.")
        build_jupyter_for_files(debug=args.debug)

    # HTML build
    if args.html:
        if args.debug:
            print("[INFO] HTML build selected.")
        if args.files:
            if args.debug:
                print(f"[INFO] Building HTML for specified files: {args.files}")
            build_html_for_files(args.files, debug=args.debug)
        else:
            if args.debug:
                print("[INFO] Building HTML for all content.")
            build_html_all(debug=args.debug)
    
    # IPYNB flat copy build
    if args.ipynb:
        cmd = [sys.executable, 'copy_ipynb_flat.py']
        if args.files:
            cmd.append('--files')
            cmd.extend(args.files)
        if args.debug:
            cmd.append('--debug')
        print(f"[INFO] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"[ERROR] copy_ipynb_flat.py failed with exit code {result.returncode}")
            sys.exit(result.returncode)
        return
    
    # Markdown build
    if args.md:
        if args.debug:
            print("[INFO] Markdown build selected.")
        if args.files:
            if args.debug:
                print(f"[INFO] Building Markdown for specified files: {args.files}")
            build_md_for_files(args.files, debug=args.debug)
        else:
            if args.debug:
                print("[INFO] Building Markdown for all content.")
            build_md_all(debug=args.debug)
    if args.docx:
        if args.debug:
            print("[INFO] DOCX build selected.")
        if args.files:
            if args.debug:
                print(f"[INFO] Building DOCX for specified files: {args.files}")
            build_docx_for_files(args.files, debug=args.debug)
        else:
            if args.debug:
                print("[INFO] Building DOCX for all content.")
            build_docx_all(debug=args.debug)
    
    if args.pdf:
        if args.debug:
            print("[INFO] PDF build selected.")
        if args.files:
            if args.debug:
                print(f"[INFO] Building PDF for specified files: {args.files}")
            build_pdf_for_files(args.files, debug=args.debug)
        else:
            if args.debug:
                print("[INFO] Building PDF for all content.")
            build_pdf_all(debug=args.debug)
    
def build_docx_all(debug=False):
    """Build DOCX for all files referenced in the menu/content tree (_content.yml)."""
    from content_parser import load_and_validate_content_yml, get_all_content_files
    content = load_and_validate_content_yml('_content.yml')
    files = get_all_content_files(content)
    if not files:
        if debug:
            print("[WARN] No files found in _content.yml toc.")
        return
    if debug:
        print(f"[INFO] Building DOCX for {len(files)} files from menu/content tree.")
    build_docx_for_files(files, debug=debug)

def build_docx_for_files(files, debug=False):
    """Build DOCX for specified markdown and notebook files."""
    import subprocess
    import sys
    import os
    from pathlib import Path
    import shutil
    import re
    repo_root = Path(__file__).parent.resolve()
    img_dir = repo_root / 'docs' / 'images'
    docx_dir = repo_root / 'docs' / 'docx'
    img_dir.mkdir(parents=True, exist_ok=True)
    docx_dir.mkdir(parents=True, exist_ok=True)
    missing_files = []
    for file in files:
        file_path = Path(file)
        if not file_path.exists():
            print(f"[ERROR] File not found: {file}")
            missing_files.append(file)
            continue
        ext = file_path.suffix.lower()
        stem = file_path.stem
        out_md = docx_dir / f"{stem}.md"
        out_docx = docx_dir / f"{stem}.docx"
        # Step 1: Ensure we have a markdown file with correct image links
        if ext == '.md':
            print(f"[INFO] Copying markdown file: {file_path} -> {out_md}")
            shutil.copy2(file_path, out_md)
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            def replace_img_link(match):
                img_path = match.group(1)
                if img_path.startswith('http'):
                    # Always replace remote images with a warning/placeholder for PDF export
                    warning = '\\n> **[Image not embedded: remote images are not included in PDF export. Check the original file for the image.]**\\n'
                    placeholder = f'![Image not embedded: remote image]({img_path})'
                    if debug:
                        print(f"[WARN] Replacing ALL remote images with placeholder: {img_path}")
                    return warning + placeholder
                img_filename = os.path.basename(img_path)
                flat_name = f"{stem}_{img_filename}"
                src_img = build_pdf_dir / img_path
                dest_img = img_dir / flat_name
                if src_img.exists():
                    shutil.copy2(src_img, dest_img)
                    if debug:
                        print(f"[INFO] Copied image {src_img} -> {dest_img}")
                rel_path = os.path.relpath(dest_img, build_pdf_dir)
                return match.group(0).replace(img_path, rel_path)
            new_md_content = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', replace_img_link, md_content)
            with open(out_md, 'w', encoding='utf-8') as f:
                f.write(new_md_content)
        elif ext == '.ipynb':
            print(f"[INFO] Converting notebook to markdown: {file_path} -> {out_md}")
            import nbformat
            import subprocess
            nb = nbformat.read(str(file_path), as_version=4)
            tmp_md = docx_dir / f"{stem}_tmp.md"
            cmd = [sys.executable, '-m', 'nbconvert', '--to', 'markdown', str(file_path), '--output', tmp_md.name, '--output-dir', str(docx_dir)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[ERROR] nbconvert failed for {file_path}: {result.stderr}")
                continue
            with open(tmp_md, 'r', encoding='utf-8') as f:
                md_content = f.read()
            def replace_img_link(match):
                img_path = match.group(1)
                if img_path.startswith('http'):
                    # Always replace remote images with a warning/placeholder for PDF export
                    warning = '\n> **[Image not embedded: remote images are not included in PDF export. Check the original file for the image.]**\n'
                    placeholder = f'![Image not embedded: remote image]({img_path})'
                    if debug:
                        print(f"[WARN] Replacing ALL remote images with placeholder: {img_path}")
                    return warning + placeholder
                img_filename = os.path.basename(img_path)
                flat_name = f"{stem}_{img_filename}"
                src_img = docx_dir / img_path
                dest_img = img_dir / flat_name
                if src_img.exists():
                    shutil.copy2(src_img, dest_img)
                    print(f"[INFO] Copied image {src_img} -> {dest_img}")
                rel_path = os.path.relpath(dest_img, docx_dir)
                return match.group(0).replace(img_path, rel_path)
            new_md_content = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', replace_img_link, md_content)
            with open(out_md, 'w', encoding='utf-8') as f:
                f.write(new_md_content)
            tmp_md.unlink()
        else:
            print(f"[SKIP] Unsupported file type: {file}")
            continue
        # Step 2: Convert markdown to docx with pandoc
        print(f"[INFO] Converting markdown to docx: {out_md} -> {out_docx}")
        cmd = ['pandoc', str(out_md), '-o', str(out_docx), '--resource-path', str(img_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] pandoc failed for {out_md}: {result.stderr}")
            continue
        print(f"[OK] Built {out_docx} from {file}")
    if missing_files:
        print(f"[SUMMARY] {len(missing_files)} file(s) were missing and not processed:")
        for mf in missing_files:
            print(f"  - {mf}")
import re
import shutil
from pathlib import Path
def build_md_all(debug=False):
    """Build Markdown for all files referenced in the menu/content tree (_content.yml)."""
    from content_parser import load_and_validate_content_yml, get_all_content_files
    content = load_and_validate_content_yml('_content.yml')
    files = get_all_content_files(content)
    if not files:
        if debug:
            print("[WARN] No files found in _content.yml toc.")
        return
    if debug:
        print(f"[INFO] Building Markdown for {len(files)} files from menu/content tree.")
    build_md_for_files(files, debug=debug)

def build_md_for_files(files, debug=False):
    """Build Markdown for specified markdown and notebook files."""
    repo_root = Path(__file__).parent.resolve()
    md_dir = repo_root / 'docs' / 'md'
    img_dir = repo_root / 'docs' / 'images'
    md_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)
    missing_files = []
    for file in files:
        file_path = Path(file)
        if not file_path.exists():
            if debug:
                print(f"[ERROR] File not found: {file}")
            missing_files.append(file)
            continue
        ext = file_path.suffix.lower()
        stem = file_path.stem
        out_md = md_dir / f"{stem}.md"
        if ext == '.md':
            print(f"[INFO] Copying markdown file: {file_path} -> {out_md}")
            shutil.copy2(file_path, out_md)
            # Copy images referenced in the markdown
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            def replace_img_link(match):
                img_path = match.group(1)
                if img_path.startswith('http'):
                    return match.group(0)
                img_filename = os.path.basename(img_path)
                flat_name = f"{stem}_{img_filename}"
                src_img = file_path.parent / img_path
                dest_img = img_dir / flat_name
                if src_img.exists():
                    shutil.copy2(src_img, dest_img)
                    print(f"[INFO] Copied image {src_img} -> {dest_img}")
                # Use ../images/ for correct relative path from docs/md/
                return match.group(0).replace(img_path, f"../images/{flat_name}")
            new_md_content = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', replace_img_link, md_content)
            with open(out_md, 'w', encoding='utf-8') as f:
                f.write(new_md_content)
        elif ext == '.ipynb':
            print(f"[INFO] Converting notebook to markdown: {file_path} -> {out_md}")
            import nbformat
            import subprocess
            nb = nbformat.read(str(file_path), as_version=4)
            tmp_md = md_dir / f"{stem}_tmp.md"
            # Use nbconvert to convert to markdown
            cmd = [sys.executable, '-m', 'nbconvert', '--to', 'markdown', str(file_path), '--output', tmp_md.name, '--output-dir', str(md_dir)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                if debug:
                    print(f"[ERROR] nbconvert failed for {file_path}: {result.stderr}")
                continue
            # Read and fix image links in the generated markdown
            with open(tmp_md, 'r', encoding='utf-8') as f:
                md_content = f.read()
            def replace_img_link(match):
                img_path = match.group(1)
                if img_path.startswith('http'):
                    return match.group(0)
                img_filename = os.path.basename(img_path)
                flat_name = f"{stem}_{img_filename}"
                src_img = md_dir / img_path
                dest_img = img_dir / flat_name
                if src_img.exists():
                    shutil.copy2(src_img, dest_img)
                    print(f"[INFO] Copied image {src_img} -> {dest_img}")
                # Use ../images/ for correct relative path from docs/md/
                return match.group(0).replace(img_path, f"../images/{flat_name}")
            new_md_content = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', replace_img_link, md_content)
            with open(out_md, 'w', encoding='utf-8') as f:
                f.write(new_md_content)
            tmp_md.unlink()  # Remove temp file
        else:
            if debug:
                print(f"[SKIP] Unsupported file type: {file}")
            continue
        print(f"[OK] Built {out_md} from {file}")
    if missing_files:
        print(f"[SUMMARY] {len(missing_files)} file(s) were missing and not processed:")
        for mf in missing_files:
            print(f"  - {mf}")

def build_pdf_all(debug=False):
    """Build PDF for all files referenced in the menu/content tree (_content.yml)."""
    from content_parser import load_and_validate_content_yml, get_all_content_files
    content = load_and_validate_content_yml('_content.yml')
    files = get_all_content_files(content)
    if not files:
        if debug:
            print("[WARN] No files found in _content.yml toc.")
        return
    if debug:
        print(f"[INFO] Building PDF for {len(files)} files from menu/content tree.")
    build_pdf_for_files(files, debug=debug)

def build_pdf_for_files(files, debug=False):
    """Build PDF for specified markdown and notebook files."""
    import subprocess
    import sys
    import os
    from pathlib import Path
    import shutil
    import re
    from sanitize_unicode import sanitize_text as sanitize_unicode
    repo_root = Path(__file__).parent.resolve()
    pdf_dir = repo_root / 'docs' / 'pdf'
    build_pdf_dir = repo_root / '_build' / 'pdf'
    img_dir = repo_root / 'docs' / 'images'
    pdf_dir.mkdir(parents=True, exist_ok=True)
    build_pdf_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)
    missing_files = []
    for file in files:
        file_path = Path(file)
        if not file_path.exists():
            if debug:
                print(f"[ERROR] File not found: {file}")
            missing_files.append(file)
            continue
        ext = file_path.suffix.lower()
        stem = file_path.stem
        out_md = build_pdf_dir / f"{stem}.md"
        out_pdf = build_pdf_dir / f"{stem}.pdf"
        # Step 1: Ensure we have a markdown file with correct image links
        if ext == '.md':
            if debug:
                print(f"[INFO] Copying markdown file: {file_path} -> {out_md}")
            shutil.copy2(file_path, out_md)
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            def replace_img_link(match):
                img_path = match.group(1)
                if img_path.startswith('http'):
                    # Always replace remote images with a warning/placeholder for PDF export
                    warning = '\n> **[Image not embedded: remote images are not included in PDF export. Check the original file for the image.]**\n'
                    placeholder = f'![Image not embedded: remote image]({img_path})'
                    if debug:
                        print(f"[WARN] Replacing ALL remote images with placeholder: {img_path}")
                    return warning + placeholder
                img_filename = os.path.basename(img_path)
                flat_name = f"{stem}_{img_filename}"
                src_img = file_path.parent / img_path
                dest_img = img_dir / flat_name
                if src_img.exists():
                    shutil.copy2(src_img, dest_img)
                    if debug:
                        print(f"[INFO] Copied image {src_img} -> {dest_img}")
                # For pdf, use relative path from build_pdf_dir to img_dir
                rel_path = os.path.relpath(dest_img, build_pdf_dir)
                return match.group(0).replace(img_path, rel_path)
            new_md_content = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', replace_img_link, md_content)
            sanitized_md_content = sanitize_unicode(new_md_content)
            with open(out_md, 'w', encoding='utf-8') as f:
                f.write(sanitized_md_content)
        elif ext == '.ipynb':
            if debug:
                print(f"[INFO] Converting notebook to markdown: {file_path} -> {out_md}")
            import nbformat
            nb = nbformat.read(str(file_path), as_version=4)
            tmp_md = build_pdf_dir / f"{stem}_tmp.md"
            cmd = [sys.executable, '-m', 'nbconvert', '--to', 'markdown', str(file_path), '--output', tmp_md.name, '--output-dir', str(build_pdf_dir)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                if debug:
                    print(f"[ERROR] nbconvert failed for {file_path}: {result.stderr}")
                continue
            with open(tmp_md, 'r', encoding='utf-8') as f:
                md_content = f.read()
            def replace_img_link(match):
                img_path = match.group(1)
                if img_path.startswith('http'):
                    # Always replace remote images with a warning/placeholder for PDF export
                    warning = '\n> **[Image not embedded: remote images are not included in PDF export. Check the original file for the image.]**\n'
                    placeholder = f'![Image not embedded: remote image]({img_path})'
                    if debug:
                        print(f"[WARN] Replacing ALL remote images with placeholder: {img_path}")
                    return warning + placeholder
                img_filename = os.path.basename(img_path)
                flat_name = f"{stem}_{img_filename}"
                src_img = build_pdf_dir / img_path
                dest_img = img_dir / flat_name
                if src_img.exists():
                    shutil.copy2(src_img, dest_img)
                    if debug:
                        print(f"[INFO] Copied image {src_img} -> {dest_img}")
                rel_path = os.path.relpath(dest_img, build_pdf_dir)
                return match.group(0).replace(img_path, rel_path)
            new_md_content = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', replace_img_link, md_content)
            with open(out_md, 'w', encoding='utf-8') as f:
                f.write(new_md_content)
            tmp_md.unlink()
        else:
            if debug:
                print(f"[SKIP] Unsupported file type: {file}")
            continue
        # Step 2: Convert markdown to pdf with pandoc
        if debug:
            print(f"[INFO] Converting markdown to pdf: {out_md} -> {out_pdf}")
        cmd = ['pandoc', str(out_md), '-o', str(out_pdf), '--resource-path', str(img_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            if debug:
                print(f"[ERROR] pandoc failed for {out_md}: {result.stderr}")
            continue
        # Copy to docs/pdf as well
        shutil.copy2(out_pdf, pdf_dir / f"{stem}.pdf")
        if debug:
            print(f"[OK] Built {out_pdf} and copied to {pdf_dir / f'{stem}.pdf'} from {file}")
    if missing_files:
        print(f"[SUMMARY] {len(missing_files)} file(s) were missing and not processed:")
        for mf in missing_files:
            print(f"  - {mf}")

if __name__ == "__main__":
    main()
