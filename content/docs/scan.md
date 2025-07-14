# OERForge Asset Scanning and Database Logic (`scan.py`)

This document provides detailed documentation for the `scan.py` module, which implements asset scanning, database population, and metadata extraction for the OERForge project. The module is responsible for reading content files, extracting assets, tracking conversion capabilities, and populating the SQLite database with robust logging and error handling.

## Table of Contents
- [Overview](#overview)
- [Key Responsibilities](#key-responsibilities)
- [Functions](#functions)
  - [log_event](#log_event)
  - [batch_read_files](#batch_read_files)
  - [read_markdown_file](#read_markdown_file)
  - [read_notebook_file](#read_notebook_file)
  - [read_docx_file](#read_docx_file)
  - [batch_extract_assets](#batch_extract_assets)
  - [extract_linked_files_from_markdown_content](#extract_linked_files_from_markdown_content)
  - [extract_linked_files_from_notebook_cell_content](#extract_linked_files_from_notebook_cell_content)
  - [extract_linked_files_from_docx_content](#extract_linked_files_from_docx_content)
  - [populate_site_info_from_config](#populate_site_info_from_config)
  - [get_possible_conversions](#get_possible_conversions)
  - [scan_toc_and_populate_db](#scan_toc_and_populate_db)
- [Workflow Example](#workflow-example)
- [Error Handling and Logging](#error-handling-and-logging)
- [Notes](#notes)

---

## Overview

`scan.py` is the main asset scanning and database population module for OERForge. It reads the Table of Contents (TOC) from `_config.yml`, walks through all referenced files, extracts assets (images, documents, etc.), determines conversion capabilities, and writes all relevant metadata to the database. It also supports robust logging and error handling for all operations.

## Key Responsibilities
- Read and parse content files (Markdown, Jupyter Notebooks, DOCX)
- Extract linked and embedded assets from content
- Track conversion capabilities for each file type
- Populate the `content` and `files` tables in the database
- Link files to pages via the `pages_files` table
- Populate site-wide metadata from configuration
- Log all operations and errors for auditability

## Functions

### log_event
```python
def log_event(message, level="INFO"):
```
Logs an event to both stdout and `scan.log` in the project root. Each entry is timestamped and includes a severity level.
- `message`: Log message
- `level`: Severity (INFO, ERROR, WARN, DEBUG)

### batch_read_files
```python
def batch_read_files(file_paths):
```
Reads multiple files and returns their contents as a dictionary `{path: content}`. Supports Markdown (`.md`), Jupyter Notebooks (`.ipynb`), DOCX (`.docx`), and other file types.
- `file_paths`: List of file paths to read

### read_markdown_file
```python
def read_markdown_file(path):
```
Reads a Markdown file and returns its content as a string.
- `path`: Path to the Markdown file

### read_notebook_file
```python
def read_notebook_file(path):
```
Reads a Jupyter Notebook file and returns its content as a dictionary.
- `path`: Path to the notebook file

### read_docx_file
```python
def read_docx_file(path):
```
Reads a DOCX file and returns its text content as a string. Requires `python-docx`.
- `path`: Path to the DOCX file

### batch_extract_assets
```python
def batch_extract_assets(contents_dict, content_type, **kwargs):
```
Extracts assets from multiple file contents in one pass. Inserts each source file as a page if not present, and extracts assets for each file type. Inserts asset records into the `files` table and links them to pages.
- `contents_dict`: `{path: content}` mapping
- `content_type`: 'markdown', 'notebook', 'docx', etc.
- `kwargs`: Optional DB connection/cursor

### extract_linked_files_from_markdown_content
```python
def extract_linked_files_from_markdown_content(md_text, page_id=None):
```
Extracts asset links from Markdown text using regex. Returns a list of asset records.
- `md_text`: Markdown content as string
- `page_id`: Optional page ID

### extract_linked_files_from_notebook_cell_content
```python
def extract_linked_files_from_notebook_cell_content(cell, nb_path=None):
```
Extracts asset links from a notebook cell, including markdown-linked images and embedded/code-produced images from outputs. Returns a list of asset records.
- `cell`: Notebook cell dictionary
- `nb_path`: Path to the notebook

### extract_linked_files_from_docx_content
```python
def extract_linked_files_from_docx_content(docx_path, page_id=None):
```
Extracts asset links from a DOCX file, including text-based links and embedded images. Returns a list of asset records.
- `docx_path`: Path to the DOCX file
- `page_id`: Optional page ID

### populate_site_info_from_config
```python
def populate_site_info_from_config(config_path):
```
Reads `_config.yml` and populates the `site_info` table with site and footer info. Also reads `header.html` for site header content.
- `config_path`: Path to the config YAML file

### get_possible_conversions
```python
def get_possible_conversions(extension):
```
Returns a dictionary of possible conversions for a given file extension. Keys include `can_convert_md`, `can_convert_tex`, `can_convert_pdf`, etc. Values are booleans indicating if conversion is possible.
- `extension`: File extension (e.g., `.md`, `.ipynb`, `.docx`)

### scan_toc_and_populate_db
```python
def scan_toc_and_populate_db(config_path):
```
Main entry point for TOC-driven asset scanning and database population. Reads the TOC from `_config.yml`, walks through all referenced files, extracts assets, determines conversion flags, and populates the database. Also handles recursive TOC structures and robust error logging.
- `config_path`: Path to the config YAML file

## Workflow Example

1. **Initialize the database (see `db_utils.py`)**
2. **Run TOC-driven scan and DB population:**
   ```python
   scan_toc_and_populate_db("_config.yml")
   ```
3. **Read and extract assets from all content files:**
   - Markdown: `batch_extract_assets(..., 'markdown', ...)`
   - Notebook: `batch_extract_assets(..., 'notebook', ...)`
   - DOCX: `batch_extract_assets(..., 'docx', ...)`
4. **Link assets to pages and update DB tables**
5. **Log all operations and errors for auditability**

## Error Handling and Logging
- All major operations are wrapped in try/except blocks with detailed error logging.
- All debug, info, and error messages are written to both stdout and `scan.log`.
- Database commits and connection management are logged with timestamps and thread/process IDs.

## Notes
- The module is designed for extensibility; new file types and asset extraction logic can be added easily.
- Conversion capability logic is centralized in `get_possible_conversions` for maintainability.
- All database operations use the robust utilities in `db_utils.py`.
- Recursive TOC structures are supported for complex content hierarchies.

---

For further details, see the source code in `oerforge/scan.py`.
