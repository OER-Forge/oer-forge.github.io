# SCAN-NOTES.md

## Modular Asset Scanning Plan (OER-Forge)

This document outlines the step-by-step plan, rationale, and implementation notes for modular asset scanning in the OER-Forge static site generator. It is intended as a reference for future development, debugging, or onboarding.

---

### 1. Database Schema Extension
- **Goal:** Track notebook assets with rich metadata.
- **Action:**
  - Extend the `files` table to include:
    - `cell_type` (Jupyter cell type: code, markdown, etc.)
    - `is_code_generated` (True if asset is expected from code execution)
    - `is_embedded` (True if asset is stored inside notebook, e.g., base64)
- **Test:** Run DB initialization and confirm schema changes.

---

### 2. Logging
- **Goal:** Robust, modular logging for all scan events.
- **Action:**
  - Implement `log_event(message, level)` to write to both stdout and a log file in the project root (e.g., `scan.log`).
  - Log all warnings, errors, and image findings.
- **Test:** Log sample messages and verify both outputs.

---

### 3. TOC Parsing
- **Goal:** Only scan notebooks listed in `toc:`.
- **Action:**
  - Implement `get_notebook_paths_from_toc(toc_path)` to parse the toc file and return a list of notebook paths.
  - Ignore notebooks not listed in toc.
- **Test:** Parse a sample toc file and confirm correct notebook list.

---

### 4. Notebook Scanning
- **Goal:** Modular, cell-by-cell asset extraction.
- **Action:**
  - Implement `scan_notebook_for_assets(nb_path)` to iterate notebook cells and call extraction logic.
  - For each cell, call `extract_images_from_notebook_cell(cell, nb_path)`.
- **Test:** Run on a sample notebook and print/log cell info.

---

### 5. Image Extraction
- **Goal:** Extract all images/files from notebook cells, with metadata.
- **Action:**
  - Implement `extract_images_from_notebook_cell(cell, nb_path)`:
    - Handles both markdown and code cells.
    - Records `cell_type`, `is_code_generated`, `is_embedded`.
    - Logs warnings if code-generated images are missing.
- **Test:** Extract images/files from sample cells, including embedded and code-generated.

---

### 6. Notebook File Insertion
- **Goal:** Insert notebook asset records with full metadata.
- **Action:**
  - Implement `insert_notebook_file_record(file_record)` to insert all fields into the DB.
- **Test:** Insert sample records and verify DB contents.

---

### 7. Integration & End-to-End Testing
- **Goal:** Validate the full workflow.
- **Action:**
  - Run the complete scan: parse toc, scan notebooks, extract assets, insert records, and log events.
- **Test:** Confirm all assets are tracked, missing/code-generated images are logged, and DB is correct.

---

## Implementation Notes
- **Modularity:** Each function is independent and testable. Debugging is easier, and future extension (e.g., for `.docx`) is straightforward.
- **Redundancy:** No major redundant functions. Consider refactoring file insertion if overlap occurs.
- **Logging:** Always to both stdout and file.
- **Schema:** Update schema before implementing asset extraction and insertion.
- **__all__ List:** Add new stubs to `__all__` if needed for external use.

---

## Next Steps
1. Extend DB schema for notebook asset fields.
2. Implement logging.
3. Implement toc parsing.
4. Implement notebook scanning.
5. Implement image extraction.
6. Implement notebook file insertion.
7. Integrate and test end-to-end.

---

## Reference: Key Functions
- `initialize_database()`
- `get_notebook_paths_from_toc(toc_path)`
- `scan_notebook_for_assets(nb_path)`
- `extract_images_from_notebook_cell(cell, nb_path)`
- `insert_notebook_file_record(file_record)`
- `log_event(message, level)`

---

## Pause/Resume Guidance
- If pausing, review this file before resuming.
- Start with the next unimplemented step in the list above.
- Use modular tests for each function before integration.

---

_Last updated: July 13, 2025_
