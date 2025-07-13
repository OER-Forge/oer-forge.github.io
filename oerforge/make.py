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

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_FILES_DIR = os.path.join(PROJECT_ROOT, 'build', 'files')
BUILD_HTML_DIR = os.path.join(PROJECT_ROOT, 'build')
LOG_PATH = os.path.join(PROJECT_ROOT, 'loh')

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

    # Inject highlight.js and MathJax
    highlight_js = (
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">\n'
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>\n'
        '<script>hljs.highlightAll();</script>'
    )
    mathjax = (
        '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
    )

    # Add ARIA attributes to code blocks
    import re
    html_body = re.sub(r'<pre><code', '<pre aria-label="Code block"><code role="code"', html_body)

    # Admonition blocks: ensure class is present
    html_body = re.sub(r'<div class="admonition', '<div class="admonition', html_body)

    # Rewrite image src paths to point to files/assets/... instead of assets/...
    def rewrite_img_src(match):
        src = match.group(1)
        # Only rewrite if src starts with 'assets/'
        if src.startswith('assets/'):
            return f'<img alt="{match.group(2)}" src="files/{src}"'
        return match.group(0)

    html_body = re.sub(r'<img alt="([^"]*)" src="([^"]+)"',
                      lambda m: f'<img alt="{m.group(1)}" src="files/{m.group(2)}"' if m.group(2).startswith('assets/') else m.group(0),
                      html_body)

    # Basic HTML template
    html_template = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='utf-8'>
        <title>{os.path.basename(md_path)}</title>
        {highlight_js}
        {mathjax}
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    # Write output
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

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
    run_make(debug=True)
