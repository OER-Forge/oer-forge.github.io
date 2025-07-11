# `scan.py`

The module `scan.py` is designed to scan and extract metadata from various content files in an Open Educational Resource (OER) project. It populates a SQLite database with structured information about the site, table of contents (TOC), pages, and images found within those pages. The module supports multiple file types including markdown, Jupyter notebooks, Word documents, LaTeX files, and PDFs.

## Why use SQLite?

SQLite is chosen for its simplicity, portability, and ease of integration. For small OER projects, SQLite provides a lightweight database solution that doesn't require a separate server, making it ideal for local development and deployment. It can be used without an internet connection, and the entire database is stored in a single file, which simplifies backup and sharing.

### SQLite Database Schema (Text Figure)

```
+-------------------+      +--------------------+
|      site         |      |        toc         |
+-------------------+      +--------------------+
| id (PK)           |      | toc_id (PK)        |
| site_title        |      | toc_filename       |
| site_subtitle     |      | toc_title          |
| site_url          |      | toc_filetype       |
| site_license      |      | toc_level          |
| site_logo         |      | toc_automated_build|
| site_favicon      |      +--------------------+
| site_theme_light  |                           
| site_theme_dark   |                           
| site_theme_default|                           
| site_footer       |                           
+-------------------+
```

```
+-------------------+      +----------------------+
|      page         |      |    page_images       |
+-------------------+      +----------------------+
| page_id (PK)      |      | id (PK)              |
| page_filename     |      | image_page_id (FK)   |
| page_title        |      | image_filename       |
| page_filetype     |      | image_remote         |
| page_convert_*    |      | image_type           |
| page_built_ok_*   |      +----------------------+
| page_wcag_ok_*    |
| page_filename_*   |
| page_level        |
| page_toc_id (FK)  |
+-------------------+
```

Legend:
- PK = Primary Key
- FK = Foreign Key
- `page_convert_*`, `page_built_ok_*`, `page_wcag_ok_*`, `page_filename_*` are sets of columns for different filetypes (md, ipynb, docx, tex, pdf, jupyter).

---

## `scan.py` Documentation Block

### Module: scan

Purpose:

  - Scans OER project configuration and content files, extracts metadata, and populates a SQLite database with structured tables for site, table of contents (TOC), pages, and page images.

Tables:
  - site: Project metadata (title, author, URL, license, logo, themes, footer).
  - toc: Table of contents entries (filename, title, filetype, level, automated build flag).
  - page: Page metadata (filename, title, filetype, conversion flags, build/WCAG status, filenames for each format, level, foreign key to TOC).
  - page_images: Image references found in content files (filename, remote flag, filetype, foreign key to page).

Key Functions:

  - initialize_database(): Creates and resets all database tables.
  - populate_site_info(): Reads and writes site metadata from config.
  - populate_toc(): Recursively populates the TOC table from config.
  - populate_page_info_from_config(): Populates the page table, sets conversion flags, links to TOC.
  - scan_all_images(): Scans all pages for images, dispatches to filetype-specific extractors.
  - extract_image_info_from_ipynb(): Extracts image references from Jupyter notebooks.
  - write_page_images_to_db(): Writes image records to the database.
  - read_page_images_from_db(): Queries image records for a given page.
  - print_table(): Prints any table in a readable format.
  - verify_toc_page_link(): Checks that page-to-TOC links are correct.

Design Notes:

  - Functions are organized for maintainability.
  - Each function includes a docstring describing its purpose, arguments, and return values.
  - Error handling is included for database operations and file parsing.
  - Foreign key relationships are enforced for data integrity.

Usage:

  - Import and call these functions from your build orchestrator (e.g., build.py) to initialize and populate the database, scan for images, and verify links.
  - Extend with additional filetype handlers as needed for markdown, docx, html, etc.

See individual function docstrings for further details.