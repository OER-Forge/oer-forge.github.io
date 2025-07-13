def convert_wcag_reports_to_html():
    print("[DEBUG] Running convert_wcag_reports_to_html...")
    src_dir = os.path.join(PROJECT_ROOT, 'build', 'files', 'wcag-reports')
    dest_dir = os.path.join(PROJECT_ROOT, 'docs', 'wcag-reports')
    if not os.path.exists(dest_dir):
        print(f"[DEBUG] Creating output directory: {dest_dir}")
        os.makedirs(dest_dir, exist_ok=True)
    """
    Convert all markdown accessibility reports in build/files/wcag-reports to HTML using site templates, saving to build/docs/wcag-reports.
    """
    import markdown
    src_dir = os.path.join(PROJECT_ROOT, 'build', 'files', 'wcag-reports')
    dest_dir = os.path.join(PROJECT_ROOT, 'docs', 'wcag-reports')
    # Always create output directory
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    # If no source directory, nothing to convert
    if not os.path.exists(src_dir):
        logging.info(f"No accessibility reports found in {src_dir}")
        return
    template_path = os.path.join(PROJECT_ROOT, 'static', 'templates', 'page.html')
    template = load_template(template_path)
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for filename in filenames:
            if filename.lower().endswith('.md'):
                src_path = os.path.join(dirpath, filename)
                # Always flatten to dest_dir, no subfolders (unless you want to preserve them)
                rel_path = os.path.relpath(src_path, src_dir)
                dest_path = os.path.join(dest_dir, os.path.splitext(rel_path)[0] + '.html')
                dest_subdir = os.path.dirname(dest_path)
                if not os.path.exists(dest_subdir):
                    os.makedirs(dest_subdir, exist_ok=True)
                with open(src_path, 'r', encoding='utf-8') as f:
                    md_text = f.read()
                html_body = markdown.markdown(md_text, extensions=['fenced_code', 'tables', 'toc', 'meta'])
                # Use first heading as title if present
                import re
                match = re.search(r'^#\s+(.+)', md_text, re.MULTILINE)
                if match:
                    title = match.group(1).strip()
                else:
                    title = filename.replace('.md', '').replace('_', ' ').title()
                header = create_header(title, '')
                footer = create_footer()
                html_output = render_page(title, html_body, header, footer, dest_path)
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(html_output)
                logging.info(f"Converted report {src_path} to {dest_path}")
def copy_wcag_reports_to_docs():
    """
    Copy all markdown accessibility reports from build/files/wcag-reports to build/docs/wcag-reports, preserving structure.
    """
    src_dir = os.path.join(PROJECT_ROOT, 'build', 'files', 'wcag-reports')
    dest_dir = os.path.join(PROJECT_ROOT, 'build', 'docs', 'wcag-reports')
    if not os.path.exists(src_dir):
        logging.info(f"No accessibility reports found in {src_dir}")
        return
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for filename in filenames:
            if filename.lower().endswith('.md'):
                src_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(src_path, src_dir)
                dest_path = os.path.join(dest_dir, rel_path)
                dest_subdir = os.path.dirname(dest_path)
                if not os.path.exists(dest_subdir):
                    os.makedirs(dest_subdir, exist_ok=True)
                shutil.copy2(src_path, dest_path)
                logging.info(f"Copied report {src_path} to {dest_path}")
import shutil
def mirror_build_to_docs():
    """Remove docs/ if exists, then copy the entire build/ folder (all files and subfolders) to docs/ in the project root."""
    docs_dir = os.path.join(PROJECT_ROOT, 'docs')
    build_dir = os.path.join(PROJECT_ROOT, 'build')
    # Remove docs_dir if exists
    if os.path.exists(docs_dir):
        shutil.rmtree(docs_dir)
    # Recursively copy build/ to docs/
    def copytree(src, dst):
        for root, dirs, files in os.walk(src):
            rel_root = os.path.relpath(root, src)
            target_root = os.path.join(dst, rel_root) if rel_root != '.' else dst
            if not os.path.exists(target_root):
                os.makedirs(target_root, exist_ok=True)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_root, file)
                shutil.copy2(src_file, dst_file)
                logging.info(f"Copied {src_file} to {dst_file}")
    copytree(build_dir, docs_dir)
"""
Prototype script to convert Markdown files in build/files to accessible standalone HTML pages in build/.

Features:
- Converts all .md files (recursively, skipping hidden files) to HTML
- Uses highlight.js for code highlighting and injects ARIA attributes
- Injects MathJax from CDN for math rendering
- Renders admonitions as <div class="admonition TYPE"> blocks
- Mirrors directory structure from build/files to build/
- Overwrites HTML files, never overwrites figures or markdown
- Logs events to project root (overwrites each run), errors also printed to console
"""

import os
import logging
import yaml
import re

# --- Project Paths and Constants ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_FILES_DIR = os.path.join(PROJECT_ROOT, 'build', 'files')
BUILD_HTML_DIR = os.path.join(PROJECT_ROOT, 'build')
LOG_PATH = os.path.join(PROJECT_ROOT, 'log')

__all__ = [
    "get_markdown_source_and_output_paths",
    "load_yaml_config",
    "ensure_build_structure",
    "convert_markdown_to_html",
    "create_section_index_html",
    "slugify"
]

# --- Logging Setup ---
def setup_logging():
    """Set up logging to overwrite log file each run."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=LOG_PATH,
        filemode='w'
    )

# --- Utility Functions ---
def slugify(title: str) -> str:
    """Convert a title to a slug suitable for folder names."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def load_yaml_config(config_path: str) -> dict:
    """Load and parse the YAML config file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logging.info(f"Loaded YAML config from {config_path}")
        return config
    except Exception as e:
        logging.error(f"Failed to load YAML config: {e}")
        return {}

def find_markdown_files(root_dir):
    """Recursively find all non-hidden .md files in root_dir."""
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.startswith('.'):
                continue
            if filename.lower().endswith('.md'):
                md_files.append(os.path.join(dirpath, filename))
    return md_files

def ensure_output_dir(md_path):
    """Ensure the output directory for the HTML file exists, mirroring build/files structure."""
    rel_path = os.path.relpath(md_path, BUILD_FILES_DIR)
    output_dir = os.path.join(BUILD_HTML_DIR, os.path.dirname(rel_path))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

# --- Template Loading and Rendering ---
def load_template(template_path: str) -> str:
    """Load the HTML template from the given path."""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def render_template(template: str, title: str, content: str) -> str:
    """Render the template with the given title and content."""
    return template.replace('{{ title }}', title).replace('{{ content }}', content)

# --- HTML Page Construction ---
def create_header(title: str, nav_html: str) -> str:
    """Generate the header HTML, including nav menu."""
    # Add theme toggle button for dark mode switching
    theme_toggle = '<button id="theme-toggle" aria-label="Switch theme" style="float:right; margin:0.5em 1em; font-size:1.5em;">🌙</button>'
    return f'<header class="site-header">\n{theme_toggle}\n<h1 class="site-title">{title}</h1>\n{nav_html}\n</header>'

def create_footer() -> str:
    """Generate the footer HTML, reading content from _config.yml if available."""
    import html
    config_path = os.path.join(PROJECT_ROOT, "_config.yml")
    config = load_yaml_config(config_path)
    footer = config.get("footer", "<!-- footer content here -->")
    # If footer is a dict, extract 'text' field
    if isinstance(footer, dict):
        footer_content = footer.get("text", "")
    else:
        footer_content = str(footer)
    # Escape HTML for safety, but allow basic tags
    safe_footer = html.escape(footer_content, quote=False)
    for tag in ["<a ", "<a>", "</a>", "<br>", "<br/>", "<strong>", "</strong>", "<em>", "</em>"]:
        safe_footer = safe_footer.replace(html.escape(tag, quote=False), tag)
    return f'<footer>\n{safe_footer}\n</footer>'

def render_page(title: str, content: str, header: str, footer: str, html_path: str) -> str:
    """Render the full HTML page using header, content, and footer."""
    template_path = os.path.join(PROJECT_ROOT, 'static', 'templates', 'page.html')
    template = load_template(template_path)
    meta = (
        '<meta name="description" content="A modern, open-source course in mathematical methods.">\n'
        '<meta name="author" content="Danny Caballero">\n'
        '<meta name="keywords" content="math, physics, open, oer">\n'
        '<meta name="robots" content="noindex,nofollow">\n'
    )
    # Compute correct relative asset path prefix based on output HTML location
    def get_asset_prefix(html_path):
        if html_path:
            html_dir = os.path.dirname(html_path)
            build_dir = os.path.join(PROJECT_ROOT, 'build')
            rel_prefix = os.path.relpath(build_dir, start=html_dir)
            if rel_prefix == '.':
                return './'
            else:
                return rel_prefix.rstrip('/') + '/'
        return './'
    rel_prefix = get_asset_prefix(html_path)
    css_links = (
        f'<link rel="stylesheet" href="{rel_prefix}css/theme-light.css" id="theme-light">\n'
        f'<link rel="stylesheet" href="{rel_prefix}css/theme-dark.css" id="theme-dark" disabled>\n'
    )
    js_links = f'<script src="{rel_prefix}js/main.js" defer></script>\n'
    # Insert CSS/JS into template only if not already present
    html = template.replace('{{ title }}', title)
    html = html.replace('{{ content }}', content)
    html = html.replace('{{ meta }}', meta)
    html = html.replace('{{ header }}', header)
    html = html.replace('{{ footer }}', footer)
    # Remove any existing theme CSS/JS links to avoid duplicates
    html = re.sub(r'<link[^>]+id="theme-light"[^>]*>', '', html)
    html = re.sub(r'<link[^>]+id="theme-dark"[^>]*>', '', html)
    html = re.sub(r'<script[^>]+src="(\.|/)js/main.js"[^>]*></script>', '', html)
    # Insert CSS/JS before closing </head>
    html = html.replace('</head>', f'{css_links}{js_links}</head>')
    return html

def generate_nav_menu(toc: list, current_folder: str = '', folder_depth: int = 0, current_html_path: str = '') -> str:
    """Generate navigation menu HTML from TOC."""
    seen_titles = set()
    nav_html = '<nav class="site-nav" role="navigation" aria-label="Main menu"><ul>'
    current_dir = os.path.dirname(current_html_path) if current_html_path else ''
    abs_current_html = os.path.abspath(current_html_path) if current_html_path else ''
    for entry in toc:
        if entry.get('menu', False):
            title = entry.get('title', '')
            if title in seen_titles:
                continue
            seen_titles.add(title)
            slug = slugify(title)
            if 'file' in entry:
                target_html = os.path.join(PROJECT_ROOT, 'build', os.path.splitext(entry['file'])[0] + '.html')
            else:
                target_html = os.path.join(PROJECT_ROOT, 'build', slug, 'index.html')
            if current_dir:
                try:
                    link = os.path.relpath(target_html, start=current_dir)
                    abs_link = os.path.abspath(os.path.join(current_dir, link))
                    mark = '✓' if os.path.exists(abs_link) else '✗'
                except Exception as e:
                    logging.error(f"[DEBUG] relpath error: {e}")
                    link = target_html
            else:
                link = target_html
            nav_html += f'<li><a href="{link}">{title}</a></li>'
    nav_html += '</ul></nav>'
    return nav_html

# --- Markdown to HTML Conversion ---
import sqlite3
def get_canonical_image_path(filename):
    db_path = os.path.join(PROJECT_ROOT, 'db', 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT image_rel_path FROM build_images WHERE image_filename = ?", (filename,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def fix_image_paths(html_body):
    """Rewrite <img> src attributes to use canonical paths from build_images DB."""
    def replacer(match):
        before = match.group(1)
        src = match.group(2)
        # Extract filename from src
        filename = os.path.basename(src)
        canonical_path = get_canonical_image_path(filename)
        if canonical_path:
            return f'<img{before}src="{canonical_path}"'
        else:
            # Optionally log missing image
            logging.warning(f"Image not found in build_images DB: {src}")
            return match.group(0)
    # Replace src in all <img ... src="..."> tags
    html_body = re.sub(r'<img([^>]+)src=["\']([^"\']+)["\']', replacer, html_body)
    return html_body

def convert_markdown_to_html(md_path, html_path):
    """Convert a markdown file to HTML and write to html_path using templates and accessibility features."""
    import markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    html_body = markdown.markdown(md_text, extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'meta'])
    html_body = html_body.replace('<table>', '<table role="table">')
    html_body = html_body.replace('<th>', '<th role="columnheader">')
    html_body = html_body.replace('<td>', '<td role="cell">')
    html_body = html_body.replace('<ul>', '<ul role="list">')
    html_body = html_body.replace('<ol>', '<ol role="list">')
    html_body = html_body.replace('<li>', '<li role="listitem">')
    html_body = html_body.replace('<nav>', '<nav role="navigation">')
    html_body = html_body.replace('<header>', '<header role="banner">')
    html_body = html_body.replace('<footer>', '<footer role="contentinfo">')
    html_body = fix_image_paths(html_body)
    mathjax_script = '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
    html_body += mathjax_script
    match = re.search(r'^#\s+(.+)', md_text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        html_body = re.sub(r'<h1[^>]*>.*?</h1>', '', html_body, count=1)
    else:
        title = "Untitled"
    config_path = os.path.join(PROJECT_ROOT, "_config.yml")
    config = load_yaml_config(config_path)
    toc = config.get("toc", [])
    toc_entry = _find_entry_by_html(html_path, toc)
    links_html = ''
    if toc_entry and 'children' in toc_entry and isinstance(toc_entry['children'], list):
        child_links = _collect_links(toc_entry['children'])
        current_dir = os.path.dirname(html_path)
        links_html = '<ul>'
        for title, target_html in child_links:
            abs_target_html = os.path.join(PROJECT_ROOT, 'build', target_html) if not os.path.isabs(target_html) else target_html
            rel_link = os.path.relpath(abs_target_html, start=current_dir)
            mark = '✓' if os.path.exists(abs_target_html) else '✗'
            links_html += f'<li><a href="{rel_link}">{title}</a> [{mark}]</li>'
        links_html += '</ul>'
        html_body += links_html
    nav_html = generate_nav_menu(toc, current_html_path=html_path)
    header = create_header(title, nav_html)
    footer = create_footer()
    html_output = render_page(title, html_body, header, footer, html_path)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_output)

def _find_entry_by_html(html_path, toc):
    """Find the TOC entry for this page."""
    html_rel = os.path.relpath(html_path, os.path.join(PROJECT_ROOT, 'build'))
    def walk(entries):
        for entry in entries:
            if 'file' in entry:
                expected_html = os.path.splitext(entry['file'])[0] + '.html'
                if expected_html == html_rel:
                    return entry
            if 'children' in entry and isinstance(entry['children'], list):
                found = walk(entry['children'])
                if found:
                    return found
        return None
    return walk(toc)

def _collect_links(entries):
    """Recursively collect child links from TOC entries."""
    links = []
    for entry in entries:
        if 'title' in entry:
            title = entry['title']
            if 'file' in entry:
                link = os.path.splitext(entry['file'])[0] + '.html'
                links.append((title, link))
            if 'children' in entry and isinstance(entry['children'], list):
                links.extend(_collect_links(entry['children']))
    return links

# --- Build Structure and TOC Functions ---
def build_all_markdown_files(source_dir, build_dir):
    """Find all markdown files in source_dir and convert them to HTML in build_dir."""
    md_files = find_markdown_files(source_dir)
    for md_path in md_files:
        rel_path = os.path.relpath(md_path, source_dir)
        output_path = os.path.join(build_dir, os.path.splitext(rel_path)[0] + '.html')
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        convert_markdown_to_html(md_path, output_path)
        logging.info(f"Converted {md_path} to {output_path}")

def create_section_index_html(section_entry, output_dir, toc):
    """Generate index.html for a section, listing links to all children and grandchildren."""
    title = section_entry.get('title', 'Section')
    child_links = _collect_links(section_entry.get('children', []))
    links_html = '<ul>'
    current_dir = output_dir
    for title, target_html in child_links:
        abs_target_html = os.path.join(PROJECT_ROOT, 'build', target_html) if not os.path.isabs(target_html) else target_html
        rel_link = os.path.relpath(abs_target_html, start=current_dir)
        mark = '✓' if os.path.exists(abs_target_html) else '✗'
        links_html += f'<li><a href="{rel_link}">{title}</a> [{mark}]</li>'
    links_html += '</ul>'
    nav_html = generate_nav_menu(toc, current_html_path=os.path.join(output_dir, 'index.html'))
    header = create_header(title, nav_html)
    footer = create_footer()
    page_html = render_page(title, links_html, header, footer, os.path.join(output_dir, 'index.html'))
    index_html_path = os.path.join(output_dir, 'index.html')
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    logging.info(f"Created section index with child links: {index_html_path}")

def get_markdown_source_and_output_paths(toc: list, files_dir: str, build_dir: str) -> list:
    """Recursively walk the toc: structure and compute source/output paths for markdown files."""
    results = []
    def walk_toc(entries, parent_path=[]):
        for entry in entries:
            current_path = parent_path.copy()
            if 'title' in entry:
                current_path.append(slugify(entry['title']))
            if 'file' in entry:
                source_md_path = os.path.join(files_dir, entry['file'])
                output_dir = os.path.join(build_dir, *current_path[:-1]) if len(current_path) > 1 else build_dir
                output_html_path = os.path.join(output_dir, os.path.splitext(os.path.basename(entry['file']))[0] + '.html')
                if not os.path.exists(source_md_path):
                    logging.error(f"Missing markdown file: {source_md_path} for toc entry: {entry.get('title', '')}")
                results.append((source_md_path, output_html_path, entry))
            if 'children' in entry and isinstance(entry['children'], list):
                walk_toc(entry['children'], current_path)
    walk_toc(toc)
    return results

def ensure_build_structure(toc: list):
    """Ensure the build/ directory mirrors the toc: structure."""
    def walk_toc(entries, parent_path=[]):
        for entry in entries:
            current_path = parent_path.copy()
            if 'title' in entry:
                current_path.append(slugify(entry['title']))
            if 'children' in entry and isinstance(entry['children'], list) and 'file' not in entry:
                output_dir = os.path.join(BUILD_HTML_DIR, *current_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    logging.info(f"Created directory for section: {output_dir}")
                create_section_index_html(entry, output_dir, toc)
                logging.info(f"Created section index with child links: {os.path.join(output_dir, 'index.html')}")
                walk_toc(entry['children'], current_path)
            elif 'children' in entry and isinstance(entry['children'], list):
                walk_toc(entry['children'], current_path)
    walk_toc(toc)

def copy_files_to_toc_structure(toc: list, files_dir: str, build_dir: str):
    """Stub: Recursively process toc: structure and copy/move files."""
    pass

def create_index_html_for_menu(title: str, header: str, footer: str, output_dir: str):
    """Stub: Create an index.html file for a top-level menu item without a file."""
    pass

# --- Main Script ---
def run_make(debug: bool = False):
    """Converts all markdown files to HTML, logs events, prints errors to console."""
    setup_logging()
    build_all_markdown_files(BUILD_FILES_DIR, BUILD_HTML_DIR)
    clean_and_copy_html_to_docs()

if __name__ == "__main__":
    setup_logging()
    config_path = os.path.join(PROJECT_ROOT, "_config.yml")
    config = load_yaml_config(config_path)
    toc = config.get("toc", [])
    files_dir = os.path.join(PROJECT_ROOT, "content")
    build_dir = os.path.join(PROJECT_ROOT, "build")
    results = get_markdown_source_and_output_paths(toc, files_dir, build_dir)
    for src, out, entry in results:
        print(f"Source: {src}\nOutput: {out}\nTOC Entry: {entry}\n")
    print("Check the log file for missing file errors.")