
# SCAN-NOTES.md

## Modular and Batch Processing Plan for Asset Scanning

### Overview
This document outlines the modular architecture and batch processing strategy for asset scanning in the OER-Forge static site generator. The goal is to maximize code reuse, extensibility, and performance for tracking and managing assets (images, files, notebooks, docx, etc.) across markdown and notebook content.

---

## Modular Functions

### 1. Content Loading
- **batch_read_files(file_paths)**
  - Reads multiple files and returns their contents as a dict: `{path: content}`.
  - Supports markdown, notebook, docx, and other file types.

### 2. Asset Extraction
- **extract_linked_files_from_content(content, content_type, **kwargs)**
  - Dispatches asset extraction based on content type (e.g., 'markdown', 'notebook_cell', 'docx').
  - Calls specialized subfunctions:
    - `extract_linked_files_from_markdown_content(md_text, page_id)`
    - `extract_linked_files_from_notebook_cell_content(cell, nb_path)`
    - `extract_linked_files_from_docx_content(docx_path, page_id)`
- **batch_extract_assets(contents_dict, content_type, **kwargs)**
  - Extracts assets from multiple file contents in one pass.
  - Returns a dict: `{path: [asset_records]}`.

### 3. Database Insertion
- **insert_file_record(file_record)**
  - Inserts a single asset record into the `files` table.
- **insert_file_records(file_records)**
  - Batch inserts multiple asset records into the `files` table.
  - Returns a list of inserted file IDs.

### 4. File-Page Linking
- **link_file_to_page(file_id, page_path)**
  - Links a single file to a page in the `pages_files` table.
- **link_files_to_pages(file_page_pairs)**
  - Batch links multiple files to pages in one transaction.
  - Accepts a list of `(file_id, page_path)` tuples.

### 5. Scanning Orchestration
- **scan_and_populate_files_db(md_dir)**
  - Orchestrates modular asset scanning for markdown, notebook, and docx files.
  - Uses batch reading, extraction, and insertion functions for efficiency.
- **scan_markdown_files(md_dir, toc_path)**
- **scan_notebook_files(notebook_paths)**
- **scan_docx_files(docx_paths)**
  - Each uses batch workflows for their respective content types.

---

## Batch Processing Benefits
- **Performance:** Fewer database transactions and file reads.
- **Clarity:** Cleaner code, easier error handling, and logging.
- **Extensibility:** Easy to add new asset/content types and batch operations.

---

## Example Workflow
1. **Batch Read:**
   - `contents = batch_read_files(file_paths)`
2. **Batch Extract:**
   - `assets_dict = batch_extract_assets(contents, content_type)`
3. **Batch Insert:**
   - `file_ids = insert_file_records(flattened_asset_list)`
4. **Batch Link:**
   - `link_files_to_pages(file_page_pairs)`

---

## Extending the System
- Add new extractors for other content types (e.g., HTML, PDF).
- Implement parallelization for large-scale batch operations.
- Modularize error handling and logging for batch functions.

---

## Summary
This modular and batch-oriented design ensures robust, maintainable, and high-performance asset management for OER-Forge. All major operations—reading, extraction, insertion, and linking—support batch processing and are easy to extend for future needs.
