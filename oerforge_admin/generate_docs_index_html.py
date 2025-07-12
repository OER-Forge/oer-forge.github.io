import os
import html
import shutil

# Paths configuration
README_PATH = "README.md"
OUTPUT_PATH = "docs/index.html"
TEMPLATE_PATH = "static/templates/readme_index.html"
CSS_SRC_DIR = "static/css"
CSS_DEST_DIR = "docs/css"
JS_SRC_DIR = "static/js"
JS_DEST_DIR = "docs/js"

def copy_assets(src_dir, dest_dir):
    """
    Copy all files from src_dir to dest_dir. Creates dest_dir if it doesn't exist.
    """
    if not os.path.exists(src_dir):
        return
    os.makedirs(dest_dir, exist_ok=True)
    for fname in os.listdir(src_dir):
        src_file = os.path.join(src_dir, fname)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, os.path.join(dest_dir, fname))

def build_index_from_readme(readme_path, output_path, template_path):
    """
    Generate an HTML index page from a Markdown README file using a template.

    Args:
        readme_path (str): Path to the README.md file.
        output_path (str): Path to write the generated HTML file.
        template_path (str): Path to the HTML template file.
    """
    if not os.path.isfile(readme_path):
        raise FileNotFoundError(f"README not found: {readme_path}")
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
    if not output_path.endswith(".html"):
        raise ValueError("Output file must be .html")

    with open(readme_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    def simple_md_to_html(md):
        """
        Convert a subset of Markdown to HTML.
        Supports headers (#, ##, ###), unordered lists (-), code blocks (```), and paragraphs.
        """
        lines = md.splitlines()
        html_lines = []
        for line in lines:
            line = html.escape(line)
            if line.startswith("# "):
                html_lines.append(f"<h1>{line[2:].strip()}</h1>")
            elif line.startswith("## "):
                html_lines.append(f"<h2>{line[3:].strip()}</h2>")
            elif line.startswith("### "):
                html_lines.append(f"<h3>{line[4:].strip()}</h3>")
            elif line.startswith("- "):
                html_lines.append(f"<li>{line[2:].strip()}</li>")
            elif line.startswith("```"):
                html_lines.append("<pre>")
            elif line == "":
                html_lines.append("<br>")
            else:
                html_lines.append(f"<p>{line}</p>")
        html_str = "\n".join(html_lines)
        html_str = html_str.replace("<li>", "<ul><li>").replace("</li>", "</li></ul>")
        html_str = html_str.replace("</ul><ul>", "")
        return html_str

    html_content = simple_md_to_html(md_content)

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    html_page = template.replace("{{ content }}", html_content)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_page)
    print(f"[INFO] Wrote {output_path}")

    # Copy CSS/JS assets
    copy_assets(CSS_SRC_DIR, CSS_DEST_DIR)
    copy_assets(JS_SRC_DIR, JS_DEST_DIR)

if __name__ == "__main__":
    build_index_from_readme(
        README_PATH,
        OUTPUT_PATH,
        TEMPLATE_PATH
    )