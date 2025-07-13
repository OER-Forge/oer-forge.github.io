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
def generate_nav_menu(toc: list) -> str:
    """
    Generate the HTML for the top-level navigation menu.
    Only includes items with menu: true.
    Uses <nav> with ARIA roles and is mobile accessible (hamburger toggle).
    Returns HTML string.
    """
    # Stub: will implement menu rendering logic
    return '<nav role="navigation" aria-label="Main menu">\n<!-- menu items here -->\n</nav>'

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
    # Stub: will use page.html template
    return f'{header}\n<main>{content}</main>\n{footer}'

# --- Markdown Conversion ---
def convert_markdown_to_html(md_path, html_path):
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

    # Load and render the template
    template_path = os.path.join(PROJECT_ROOT, 'static', 'templates', 'page.html')
    template = load_template(template_path)
    html_output = render_template(template, title, html_body)

    # Write output
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_output)

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
                if not os.path.exists(source_md_path):
                    logging.error(f"Missing markdown file: {source_md_path} for toc entry: {entry.get('title', '')}")
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
    # Stub: will implement directory and file creation logic
    pass

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
    md_files = find_markdown_files(BUILD_FILES_DIR)
    for md_path in md_files:
        try:
            # Compute output HTML path
            rel_path = os.path.relpath(md_path, BUILD_FILES_DIR)
            html_path = os.path.join(BUILD_HTML_DIR, os.path.splitext(rel_path)[0] + '.html')
            ensure_output_dir(md_path)
            convert_markdown_to_html(md_path, html_path)
            logging.info(f"Converted {md_path} to {html_path}")
        except Exception as e:
            logging.error(f"Failed to convert {md_path}: {e}")
            print(f"[ERROR] Failed to convert {md_path}: {e}")

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
