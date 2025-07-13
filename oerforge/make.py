# --- Build All Markdown Files ---
def build_all_markdown_files(source_dir, build_dir):
    """
    Find all markdown files in source_dir, compute their output locations in build_dir,
    and convert them to HTML using templates and accessibility features.
    Mirrors directory structure and changes .md to .html.
    """
    md_files = find_markdown_files(source_dir)
    for md_path in md_files:
        rel_path = os.path.relpath(md_path, source_dir)
        output_path = os.path.join(build_dir, os.path.splitext(rel_path)[0] + '.html')
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        convert_markdown_to_html(md_path, output_path)
        logging.info(f"Converted {md_path} to {output_path}")
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

# --- Markdown to HTML Conversion ---
def convert_markdown_to_html(md_path, html_path):
    """
    Convert a markdown file to HTML and write to html_path using templates and accessibility features.
    """
    import markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    # Convert markdown to HTML
    html_body = markdown.markdown(md_text, extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'meta'])
    # Accessibility and ARIA attributes
    html_body = html_body.replace('<table>', '<table role=\"table\">')
    html_body = html_body.replace('<th>', '<th role=\"columnheader\">')
    html_body = html_body.replace('<td>', '<td role=\"cell\">')
    html_body = html_body.replace('<ul>', '<ul role=\"list\">')
    html_body = html_body.replace('<ol>', '<ol role=\"list\">')
    html_body = html_body.replace('<li>', '<li role=\"listitem\">')
    html_body = html_body.replace('<nav>', '<nav role=\"navigation\">')
    html_body = html_body.replace('<header>', '<header role=\"banner\">')
    html_body = html_body.replace('<footer>', '<footer role=\"contentinfo\">')
    # MathJax
    mathjax_script = '<script src=\"https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js\"></script>'
    html_body += mathjax_script
    # Extract first markdown heading as title
    import re
    match = re.search(r'^#\\s+(.+)', md_text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        html_body = re.sub(r'<h1[^>]*>.*?</h1>', '', html_body, count=1)
    else:
        title = "Untitled"
    # Navigation
    config_path = os.path.join(PROJECT_ROOT, "_config.yml")
    config = load_yaml_config(config_path)
    toc = config.get("toc", [])
    # Compute folder depth and current folder name
    rel_html_path = os.path.relpath(html_path, BUILD_HTML_DIR)
    parts = rel_html_path.split(os.sep)
    if len(parts) > 1:
        current_folder = parts[0]
        folder_depth = len(parts) - 1
    else:
        current_folder = ''
        folder_depth = 0
    nav_html = generate_nav_menu(toc, current_folder, folder_depth)
    header = create_header(title, nav_html)
    footer = create_footer()
    html_output = render_page(title, html_body, header, footer)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_output)

# --- Logging Setup ---
def setup_logging():
    """
    Set up logging to overwrite log file each run.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=LOG_PATH,
        filemode='w'
    )

# --- Utility Functions ---
def load_yaml_config(config_path: str) -> dict:
    """
    Load and parse the YAML config file with strict ordering using PyYAML.
    Returns the config as a dictionary.
    Logs errors if parsing fails.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logging.info(f"Loaded YAML config from {config_path}")
        return config
    except Exception as e:
        logging.error(f"Failed to load YAML config: {e}")
        return {}

def slugify(title: str) -> str:
    """
    Convert a title to a slug suitable for folder names.
    Handles spaces, capitalization, and special characters.
    Example: 'A Big BluE MOuSe!' -> 'a-big-blue-mouse'
    """
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug

def find_markdown_files(root_dir):
    """
    Recursively find all non-hidden .md files in root_dir.
    Returns a list of absolute file paths.
    """
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.startswith('.'):
                continue
            if filename.lower().endswith('.md'):
                md_files.append(os.path.join(dirpath, filename))
    return md_files

def ensure_output_dir(md_path):
    """
    Ensure the output directory for the HTML file exists, mirroring build/files structure.
    """
    # Compute relative path from build/files
    rel_path = os.path.relpath(md_path, BUILD_FILES_DIR)
    # Remove filename, keep directory
    output_dir = os.path.join(BUILD_HTML_DIR, os.path.dirname(rel_path))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

# --- Template Loading and Rendering ---
def load_template(template_path: str) -> str:
    """
    Load the HTML template from the given path.
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def render_template(template: str, title: str, content: str) -> str:
    """
    Render the template with the given title and content.
    """
    return template.replace('{{ title }}', title).replace('{{ content }}', content)

# --- HTML Page Construction ---
def generate_nav_menu(toc: list, current_folder: str = '', folder_depth: int = 0, current_html_path: str = '') -> str:
    seen_titles = set()
    nav_html = '<nav role="navigation" aria-label="Main menu"><ul>'
    current_dir = os.path.dirname(current_html_path)
    logging.debug(f"[DEBUG] generate_nav_menu: current_folder={current_folder}, folder_depth={folder_depth}, current_html_path={current_html_path}, current_dir={current_dir}")
    print(f"[DEBUG] generate_nav_menu: current_folder={current_folder}, folder_depth={folder_depth}, current_html_path={current_html_path}, current_dir={current_dir}")
    for entry in toc:
        if entry.get('menu', False):
            title = entry.get('title', '')
            if title in seen_titles:
                continue
            seen_titles.add(title)
            slug = slugify(title)
            # Determine target HTML path for this menu item
            if 'file' in entry:
                target_html = os.path.splitext(entry['file'])[0] + '.html'
            else:
                target_html = os.path.join(slug, 'index.html')
            logging.debug(f"[DEBUG] Menu item: title={title}, slug={slug}, target_html={target_html}")
            print(f"[DEBUG] Menu item: title={title}, slug={slug}, target_html={target_html}")
            # Compute relative path from current page to target
            if current_dir:
                try:
                    link = os.path.relpath(target_html, start=current_dir)
                except Exception as e:
                    logging.error(f"[DEBUG] relpath error: {e}")
                    print(f"[DEBUG] relpath error: {e}")
                    link = target_html
            else:
                link = target_html
            logging.debug(f"[DEBUG] Computed link for '{title}': {link}")
            print(f"[DEBUG] Computed link for '{title}': {link}")
            nav_html += f'<li><a href="{link}">{title}</a></li>'
    nav_html += '</ul></nav>'
    return nav_html

def create_header(title: str, nav_html: str) -> str:
    """
    Generate the header HTML, including nav menu.
    Returns HTML string.
    """
    # Stub: will load header.html or build header string
    return f'<header>\n<h1>{title}</h1>\n{nav_html}\n</header>'

def create_footer() -> str:
    """
    Generate the footer HTML.
    Returns HTML string.
    """
    # Stub: will load footer.html or build footer string
    return '<footer>\n<!-- footer content here -->\n</footer>'

def render_page(title: str, content: str, header: str, footer: str) -> str:
    """
    Render the full HTML page using header, content, and footer.
    Returns HTML string.
    """
    # Load page.html template
    template_path = os.path.join(PROJECT_ROOT, 'static', 'templates', 'page.html')
    template = load_template(template_path)
    # Add SEO meta tags and dummy metadata
    meta = (
        '<meta name="description" content="A modern, open-source course in mathematical methods.">\n'
        '<meta name="author" content="Danny Caballero">\n'
        '<meta name="keywords" content="math, physics, open, oer">\n'
        '<meta name="robots" content="noindex,nofollow">\n'
    )

    # Replace placeholders in template
    html = template.replace('{{ title }}', title)
    html = html.replace('{{ content }}', content)
    html = html.replace('{{ meta }}', meta)
    html = html.replace('{{ header }}', header)
    html = html.replace('{{ footer }}', footer)
    return html
    """
    Convert a Markdown file to HTML.
    - Use highlight.js for code blocks, add ARIA attributes
    - Inject MathJax CDN script
    - Render admonitions as <div class="admonition TYPE"> blocks
    - Write output to html_path, overwriting if exists
    """
    import markdown
    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Markdown extensions for tables, code highlighting, admonitions, etc.
    extensions = [
        'extra',
        'codehilite',
        'tables',
        'toc',
        'admonition',
    ]
    extension_configs = {
        'codehilite': {
            'guess_lang': False,
            'pygments_style': 'default',
            'noclasses': True
        }
    }

    # Convert markdown to HTML
    html_body = markdown.markdown(md_text, extensions=extensions, extension_configs=extension_configs)

    # Add ARIA attributes to code blocks
    html_body = re.sub(r'<pre><code', '<pre aria-label="Code block"><code role="code"', html_body)

    # Admonition blocks: ensure class is present
    html_body = re.sub(r'<div class="admonition', '<div class="admonition', html_body)

    # Rewrite image src paths to point to files/assets/... instead of assets/...
    html_body = re.sub(
        r'<img alt="([^"]*)" src="([^"]+)"',
        lambda m: f'<img alt="{m.group(1)}" src="files/{m.group(2)}"' if m.group(2).startswith('assets/') else m.group(0),
        html_body
    )

    # Extract first markdown heading as title
    match = re.search(r'^#\s+(.+)', md_text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # Remove the first <h1> from the HTML body to avoid duplication
        html_body = re.sub(r'<h1[^>]*>.*?</h1>', '', html_body, count=1)
    else:
        title = "Untitled"

    # Generate navigation
    config_path = os.path.join(PROJECT_ROOT, "_config.yml")
    config = load_yaml_config(config_path)
    toc = config.get("toc", [])
    nav_html = generate_nav_menu(toc)
    header = create_header(title, nav_html)
    footer = create_footer()
    html_output = render_page(title, html_body, header, footer)

    # Write output
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
def create_section_index_html(section_entry, output_dir, toc):
    """
    Generate index.html for a section, listing links to all children and grandchildren.
    """
    title = section_entry.get('title', 'Section')
    # Recursively collect child links
    def collect_links(entries, parent_path=[]):
        links = []
        for entry in entries:
            current_path = parent_path.copy()
            if 'title' in entry:
                current_path.append(slugify(entry['title']))
            if 'file' in entry:
                # Output HTML path
                link = os.path.splitext(entry['file'])[0] + '.html'
                links.append((entry.get('title', ''), link))
            if 'children' in entry and isinstance(entry['children'], list):
                links.extend(collect_links(entry['children'], current_path))
        return links
    child_links = collect_links(section_entry.get('children', []))
    # Build HTML list
    links_html = '<ul>' + ''.join([f'<li><a href="{link}">{title}</a></li>' for title, link in child_links]) + '</ul>'
    nav_html = generate_nav_menu(toc)
    header = create_header(title, nav_html)
    footer = create_footer()
    page_html = render_page(title, links_html, header, footer)
    index_html_path = os.path.join(output_dir, 'index.html')
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    logging.info(f"Created section index with child links: {index_html_path}")

# --- TOC and Build Structure Functions ---
def get_markdown_source_and_output_paths(toc: list, files_dir: str, build_dir: str) -> list:
    """
    Recursively walk the toc: structure.
    For each menu item with a file:, compute:
      - The source markdown file path in files_dir (using the file: value).
      - The output HTML path in build_dir (mirroring toc: hierarchy and slugification).
    Returns a list of (source_md_path, output_html_path, toc_entry) tuples for conversion.
    Logs missing files and errors.
    """
    results = []
    def walk_toc(entries, parent_path=[]):
        for entry in entries:
            # Compute the output directory path from parent_path and slugified title
            current_path = parent_path.copy()
            if 'title' in entry:
                current_path.append(slugify(entry['title']))
            # If this entry has a file, compute source and output paths
            if 'file' in entry:
                source_md_path = os.path.join(files_dir, entry['file'])
                output_dir = os.path.join(build_dir, *current_path[:-1]) if len(current_path) > 1 else build_dir
                output_html_path = os.path.join(output_dir, os.path.splitext(os.path.basename(entry['file']))[0] + '.html')
                debug_msg = f"[DEBUG] TOC entry: title={entry.get('title', '')}, file={entry['file']}, source_md_path={source_md_path}, output_html_path={output_html_path}"
                logging.debug(debug_msg)
                print(debug_msg)
                if not os.path.exists(source_md_path):
                    logging.error(f"[DEBUG] Missing markdown file: {source_md_path} for toc entry: {entry.get('title', '')}")
                    print(f"[DEBUG] Missing markdown file: {source_md_path} for toc entry: {entry.get('title', '')}")
                results.append((source_md_path, output_html_path, entry))
            # If this entry has children, recurse
            if 'children' in entry and isinstance(entry['children'], list):
                walk_toc(entry['children'], current_path)
    walk_toc(toc)
    return results

def copy_files_to_toc_structure(toc: list, files_dir: str, build_dir: str):
    """
    Recursively process toc: structure.
    For each menu item with a file:, copy or move the corresponding .md or .ipynb (converted to .html) from files_dir to the correct folder in build_dir (mirroring toc: hierarchy).
    Logs all actions and errors.
    """
    # Stub: will implement file copying/moving logic
    pass

def ensure_build_structure(toc: list):
    """
    Ensure the build/ directory mirrors the toc: structure.
    Creates empty directories and index.html files for top-level menu items without files.
    Logs all actions.
    """
    def walk_toc(entries, parent_path=[]):
        for entry in entries:
            current_path = parent_path.copy()
            if 'title' in entry:
                current_path.append(slugify(entry['title']))
            # If this entry has children but no file, create directory and index.html
            if 'children' in entry and isinstance(entry['children'], list) and 'file' not in entry:
                output_dir = os.path.join(BUILD_HTML_DIR, *current_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    logging.info(f"Created directory for section: {output_dir}")
                # Create index.html for section
                header = create_header(entry.get('title', 'Section'), generate_nav_menu(toc))
                footer = create_footer()
                index_html_path = os.path.join(output_dir, 'index.html')
                page_html = render_page(entry.get('title', 'Section'), '', header, footer)
                with open(index_html_path, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                logging.info(f"Created index.html for section: {index_html_path}")
                # Recurse into children
                walk_toc(entry['children'], current_path)
            elif 'children' in entry and isinstance(entry['children'], list):
                # If entry has both file and children, just recurse
                walk_toc(entry['children'], current_path)
    walk_toc(toc)

def create_index_html_for_menu(title: str, header: str, footer: str, output_dir: str):
    """
    Create an index.html file for a top-level menu item without a file.
    The page contains the title and blank content, with header/footer.
    Logs creation.
    """
    # Stub: will implement file writing logic
    pass

# --- Main Script ---
def run_make(debug: bool = False):
    """
    Converts all markdown files to HTML, logs events, prints errors to console.
    Can be called from build.py or CLI.
    """
    setup_logging()
    # Use build_all_markdown_files to process all markdown files in build/files
    build_all_markdown_files(BUILD_FILES_DIR, BUILD_HTML_DIR)
    # The previous logic is now handled by build_all_markdown_files

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
