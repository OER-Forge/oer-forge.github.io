# Modern Mathematical Methods Build System

This repository contains scripts and tools for building and managing the Modern Mathematical Methods open-physics-ed content. The build system supports multiple output formats (HTML, LaTeX, PDF, DOCX, Markdown, Jupyter Book, and more) from a single source of truth, using a YAML-driven content tree and flexible Python scripts.

## Key Features

- **YAML-driven content tree**: _content.yml defines the structure and order of all content.
- **Multiple output formats**: Build HTML, LaTeX, PDF, DOCX, Markdown, Jupyter Book, and more.
- **Notebook and Markdown support**: Handles both `.md` and `.ipynb` files, including image management.
- **Static asset management**: Copies CSS and images to the correct output locations.
- **Jupyter Book integration**: Automated build and validation of Jupyter Book outputs.
- **Flexible CLI**: Build all outputs or only specific formats/files with command-line flags.

## Quick Start

1. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   # For Jupyter Book outputs:
   pip install jupyter-book
   ```

2. **Build all outputs**
   ```sh
   python build.py --all
   ```

3. **Build specific outputs**
   - HTML: `python build.py --html`
   - LaTeX: `python build.py --tex`
   - PDF: `python build.py --pdf`
   - DOCX: `python build.py --docx`
   - Markdown: `python build.py --md`
   - Jupyter Book: `python build.py --jupyter`
   - Copy flat notebooks: `python build.py --ipynb`
   - Build only specific files: `python build.py --files file1.md file2.ipynb`

4. **Debugging**
   Add `--debug` to any command for verbose output:
   ```sh
   python build.py --all --debug
   ```

## Directory Structure

- build.py — Main build script (see CLI options above)
- content — Source markdown and notebook files
- docs — Output directory for built files (HTML, LaTeX, etc.)
- static — CSS, images, and HTML templates
- scripts — Helper scripts for YAML, markdown, and notebook processing
- _content.yml — Main content tree (table of contents)
- _toc.yml — Jupyter Book TOC (auto-generated)

## Build Script Overview

- **build.py**: Main entry point. Handles argument parsing and orchestrates all build steps.
- **build_tex_all**: Builds LaTeX for all files in the content tree.
- **build_html_all**: Builds HTML for all files, using templates and navigation.
- **build_jupyter_for_files**: Orchestrates Jupyter Book build, including kernel fixes and validation.
- **copy_static_assets**: Copies CSS and images to output locations.

## Adding Content

- Add new `.md` or `.ipynb` files to the content directory.
- Update _content.yml to include new files in the correct order/structure.
- Run the build script to generate outputs.

## Troubleshooting

- If you see missing file errors, check that all files referenced in _content.yml exist.
- For Jupyter Book errors, ensure all notebooks have valid kernels and metadata.
- For LaTeX/PDF builds, ensure `pandoc` and a LaTeX distribution are installed.

## License

See LICENSE for details.

---

*For more details, see comments in build.py and the scripts in scripts.*# oer-forge
