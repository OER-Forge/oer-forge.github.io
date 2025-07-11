def copy_images_for_ipynb(ipynb_path):
    """
    Copies all images referenced by a notebook (from the page_images table) to the build/files/ directory,
    preserving the user's organization. Checks if the image file exists and handles missing files gracefully.
    """
    import os
    import sqlite3
    import shutil

    # Connect to the sqlite database
    conn = sqlite3.connect('db/sqlite.db')
    cursor = conn.cursor()

    # Get the page_id for this notebook
    cursor.execute("SELECT page_id FROM page WHERE page_filename=?", (ipynb_path,))
    page_row = cursor.fetchone()
    if not page_row:
        print(f"[WARNING] No page entry found for {ipynb_path}")
        return
    page_id = page_row[0]

    # Get all image filenames for this page
    cursor.execute("SELECT image_filename FROM page_images WHERE image_page_id=?", (page_id,))
    images = cursor.fetchall()
    conn.close()

    # Determine output directory in build/files/ preserving structure
    rel_path = os.path.relpath(ipynb_path, 'content')
    build_dir = os.path.join('build/files', os.path.dirname(rel_path))
    os.makedirs(build_dir, exist_ok=True)

    # Copy each image to the build directory
    print(f"[DEBUG] ipynb_path: {ipynb_path}")
    print(f"[DEBUG] build_dir: {build_dir}")
    for img_tuple in images:
        img = img_tuple[0]
        print(f"[DEBUG] ---")
        print(f"[DEBUG] Processing image ref: {img}")
        notebook_dir = os.path.dirname(ipynb_path)
        print(f"[DEBUG] notebook_dir: {notebook_dir}")
        src_path = os.path.normpath(os.path.join(notebook_dir, img))
        print(f"[DEBUG] Formed src_path: {src_path}")
        dest_path = os.path.join(build_dir, os.path.basename(img))
        print(f"[DEBUG] dest_path: {dest_path}")
        print(f"[DEBUG] Exists? {os.path.exists(src_path)}")
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"[INFO] Copied image {src_path} to {dest_path}")
        else:
            print(f"[WARNING] Image {src_path} not found for {ipynb_path} (tried {src_path})")
def ipynb_to_docx(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a DOCX file using nbconvert and Pandoc.
    Reuses ipynb_to_md for markdown conversion."""
    import os
    import subprocess

    # Get markdown path by calling ipynb_to_md
    md_path = ipynb_to_md(ipynb_path, output_path)
    docx_path = os.path.splitext(md_path)[0] + '.docx'

    # Use Pandoc to convert markdown to docx
    subprocess.run(['pandoc', md_path, '-o', docx_path], check=True)

    return docx_path

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
    cursor.execute("SELECT page_filename FROM page WHERE page_filename=?", (ipynb_path,))
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
