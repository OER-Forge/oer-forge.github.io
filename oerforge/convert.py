def ipynb_to_docx(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a DOCX file."""
    pass

def ipynb_to_md(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a Markdown file.
    Queries sqlite for file info and writes to build/files/ preserving user organization."""
    import os
    import sqlite3
    import nbformat
    from nbconvert import MarkdownExporter

    # Connect to the sqlite database
    conn = sqlite3.connect('db/sqlite.db')
    cursor = conn.cursor()

    # Query for the file's info (assuming a table 'page' with a column 'filepath')
    cursor.execute("SELECT filepath FROM page WHERE filepath=?", (ipynb_path,))
    result = cursor.fetchone()
    if not result:
        raise FileNotFoundError(f"File {ipynb_path} not found in database.")
    original_path = result[0]

    # Determine output path in build/files/ preserving structure
    rel_path = os.path.relpath(original_path, 'content')
    md_path = os.path.splitext(rel_path)[0] + '.md'
    output_full_path = os.path.join('build/files', md_path)
    os.makedirs(os.path.dirname(output_full_path), exist_ok=True)

    # Convert ipynb to markdown
    with open(ipynb_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    exporter = MarkdownExporter()
    body, _ = exporter.from_notebook_node(nb)

    # Write markdown to output
    with open(output_full_path, 'w', encoding='utf-8') as f:
        f.write(body)

    # Optionally return the output path
    return output_full_path

def ipynb_to_tex(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a LaTeX file."""
    pass

def ipynb_to_pdf(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a PDF file."""
    pass

def md_to_docx(md_path, output_path):
    """Convert a Markdown file (.md) to a DOCX file."""
    pass

def md_to_tex(md_path, output_path):
    """Convert a Markdown file (.md) to a LaTeX file."""
    pass

def md_to_pdf(md_path, output_path):
    """Convert a Markdown file (.md) to a PDF file."""
    pass

def docx_to_md(docx_path, output_path):
    """Convert a DOCX file to a Markdown file (.md)."""
    pass

def docx_to_pdf(docx_path, output_path):
    """Convert a DOCX file to a PDF file."""
    pass
