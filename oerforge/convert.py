def copy_images_for_ipynb(ipynb_path):
    """
    Copies all images referenced by a notebook (from the page_images table) to the build/files/ directory,
    preserving the user's organization. Checks if the image file exists and handles missing files gracefully.
    """
    pass
            
def ipynb_to_docx(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a DOCX file using nbconvert and Pandoc.
    Reuses ipynb_to_md for markdown conversion."""
    
    pass

def ipynb_to_md(ipynb_path, output_path):
    """Convert a Jupyter notebook (.ipynb) to a Markdown file.
    Queries sqlite for file info and writes to build/files/ preserving user organization."""
    

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
