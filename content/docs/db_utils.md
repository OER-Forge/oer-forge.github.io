# OERForge Database Utilities

This document provides detailed documentation for the database utility functions in `db_utils.py`, which support asset tracking, metadata management, and site configuration for the OERForge project. These utilities are designed to work with a SQLite database located at `<project_root>/db/sqlite.db`.

## Table of Contents
- [Overview](#overview)
- [Database Schema](#database-schema)
- [Functions](#functions)
  - [initialize_database](#initialize_database)
  - [log_event](#log_event)
  - [get_db_connection](#get_db_connection)
  - [insert_records](#insert_records)
  - [link_files_to_pages](#link_files_to_pages)
  - [pretty_print_table](#pretty_print_table)

---

## Overview

`db_utils.py` provides a set of functions for initializing, managing, and interacting with the OERForge SQLite database. The database tracks files/assets, their relationships to pages, content conversion status, and site-wide metadata. These utilities are used throughout the OERForge codebase for robust, auditable data workflows.

## Database Schema

The database consists of the following tables:

- **files**: Metadata about tracked files/assets (images, documents, etc.)
- **pages_files**: Maps files to pages where they are referenced
- **content**: Tracks source and output paths for content, conversion flags, and status
- **site_info**: Stores site-wide metadata and configuration

Each table is created with appropriate columns for asset tracking, conversion status, and relationships.

## Functions

### initialize_database
```python
def initialize_database():
```
Initializes the SQLite database for asset tracking. Drops existing tables and recreates them to ensure a clean state. Creates the following tables:
- `files`
- `pages_files`
- `content`
- `site_info`

**Usage:**
```python
initialize_database()
```

### log_event
```python
def log_event(message, level="INFO"):
```
Logs an event to both stdout and a log file (`db.log`) in the project root. Each log entry is timestamped and includes a severity level.
- `message`: The log message
- `level`: Severity (e.g., "INFO", "ERROR", "WARNING")

**Usage:**
```python
log_event("Database initialized.", level="INFO")
```

### get_db_connection
```python
def get_db_connection(db_path=None):
```
Returns a `sqlite3.Connection` object to the database. If `db_path` is not provided, defaults to `<project_root>/db/sqlite.db`.
- `db_path`: Optional path to the database file

**Usage:**
```python
conn = get_db_connection()
```

### insert_records
```python
def insert_records(table_name, records, db_path=None, conn=None, cursor=None):
```
General-purpose batch insert for any table. Checks if the table exists, inserts records, and returns a list of inserted row IDs.
- `table_name`: Name of the table to insert into
- `records`: List of dictionaries, each containing column-value pairs
- `db_path`: Optional path to the database file
- `conn`, `cursor`: Optional existing connection/cursor

**Returns:**
- List of inserted row IDs

**Usage:**
```python
row_ids = insert_records('files', file_records)
```

### link_files_to_pages
```python
def link_files_to_pages(file_page_pairs, db_path=None, conn=None, cursor=None):
```
Inserts mappings between file IDs and page paths into the `pages_files` table. Used to track which files are referenced by which pages.
- `file_page_pairs`: List of tuples `(file_id, page_path)`
- `db_path`, `conn`, `cursor`: Optional database connection parameters

**Usage:**
```python
link_files_to_pages([(file_id, page_path)])
```

### pretty_print_table
```python
def pretty_print_table(table_name, db_path=None, conn=None, cursor=None):
```
Prints the contents of a table in a readable, column-aligned format to stdout and the log. Useful for debugging and inspection.
- `table_name`: Name of the table to print
- `db_path`, `conn`, `cursor`: Optional database connection parameters

**Usage:**
```python
pretty_print_table('content')
```

---

## Example Workflow

1. **Initialize the database:**
   ```python
   initialize_database()
   ```
2. **Insert asset records:**
   ```python
   file_records = [{...}, {...}]
   insert_records('files', file_records)
   ```
3. **Link files to pages:**
   ```python
   link_files_to_pages([(file_id, page_path)])
   ```
4. **Print table contents:**
   ```python
   pretty_print_table('files')
   ```

---

## Notes
- All database operations are logged for auditability.
- Functions accept optional connection/cursor arguments for transaction control.
- The schema supports robust asset tracking, conversion status, and site configuration.

---

For further details, see the source code in `oerforge/db_utils.py`.
