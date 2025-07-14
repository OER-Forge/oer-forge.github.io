# convert.py: Batch Conversion and Asset Management

## Overview
`convert.py` is the main batch conversion and asset management script for the OER Forge build system. It automates the conversion of Jupyter notebooks and Markdown files, manages image extraction and copying, and updates a SQLite database with conversion status. The script is designed to mirror the Table of Contents (TOC) hierarchy, ensuring all referenced files and images are correctly processed and linked.

## Key Features
- **Batch Conversion:** Processes all files listed in the TOC, copying them to the build directory and preserving hierarchy.
- **Image Extraction and Copying:** Finds all images referenced in content files, copies them to a flat `build/images/` directory, and updates markdown image links to use correct relative paths.
- **Markdown Link Rewriting:** Ensures all image references in markdown files use the format `../../images/<filename>`, regardless of directory depth.
- **Database Integration:** Uses SQLite to track content, images, and conversion status, enabling robust asset mapping and error logging.
- **Format Conversion Stubs:** Provides functions for converting markdown to DOCX, PDF, and LaTeX using Pandoc (DOCX implemented, PDF/LaTeX are stubs).
- **Logging:** All actions and errors are logged for traceability and debugging.

## Main Components
### Constants
Defines paths for the database, content, build output, images, and logs.

### Image Handling Functions
- `query_images_for_content(content_record, conn)`: Queries the database for all images associated with a content file.
- `copy_images_to_build(images, images_root, conn)`: Copies images to the build images directory, resolving source paths using the database.
- `update_markdown_image_links(md_path, images, images_root)`: Updates image links in markdown files to use the correct relative path (`../../images/<filename>`), using the database for mapping.
- `handle_images_for_markdown(content_record, conn)`: Orchestrates image handling for a markdown file: queries, copies, and updates links.

### Conversion Functions
- `convert_md_to_docx(content_record, conn)`: Converts markdown to DOCX using Pandoc, updates the database.
- `convert_md_to_pdf(content_record, conn)`: Stub for PDF conversion.
- `convert_md_to_tex(content_record, conn)`: Stub for LaTeX conversion.

### Batch Conversion Orchestrator
- `batch_convert_all_content()`: Main entry point. Walks the TOC, copies files, processes images, and updates markdown links. Logs all actions and errors.

## Workflow
1. **TOC Parsing:** Reads `_config.yml` to get the TOC and determine which files to process.
2. **File Copying:** Copies each referenced file to `build/files/`, preserving the TOC hierarchy.
3. **Image Handling:** For each file, queries the database for referenced images, copies them to `build/images/`, and updates markdown links.
4. **Format Conversion:** Converts markdown files to DOCX (and stubs for PDF/LaTeX).
5. **Logging:** All steps are logged for debugging and traceability.

## Example: Image Link Rewriting
When processing a markdown file, all image references are rewritten to use the format:
```markdown
![Alt Text](../../images/filename.png)
```
This ensures that image links work regardless of the markdown file's location in the hierarchy.

## Error Handling
- Missing files or images are logged as errors.
- Database lookup failures are logged.
- Copy failures are logged with details.

## Extending
- Implement PDF and LaTeX conversion stubs as needed.
- Add support for other asset types or formats.
- Enhance logging and validation as required.

## Usage
Run the script directly to process all content:
```bash
python oerforge/convert.py
```

## Author
[Your Name]
