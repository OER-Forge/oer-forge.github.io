# CONVERT-NOTES.md

## Purpose
This file documents the ongoing development, debugging, and enhancement of the batch conversion and image handling logic in OER-Forge. It is intended to provide a detailed, chronological record of all major changes, problems encountered, solutions implemented, and lessons learned.

---

## Chronology & Milestones

### 1. Initial Batch Conversion Logic
- The original `convert.py` only copied `.md` files referenced in the TOC to `build/files/`, preserving the TOC hierarchy.
- Validation was performed using a test harness in `build-test.py`.

### 2. Expanding File Copying
- Requirement: Copy all files referenced in the TOC (not just markdown) to `build/files/`, preserving hierarchy.
- Patched `convert.py` to iterate over all TOC-referenced files and copy them.
- Updated `build-test.py` to validate presence of all files.
- Result: All TOC-referenced files are now copied correctly.

### 3. Image Copy Logic
- Requirement: Copy all images referenced in content (using SQLite DB) flat to `build/images/`.
- Initial implementation used image paths from the DB, but failed due to incorrect path resolution.
- Validation: No images appeared in `build/images/`.

### 4. Debugging Image Path Resolution
- Problem: Image paths in the DB are relative to the source file, not the project root.
- Solution: Compute the absolute path for each image by resolving its relative path against the directory of its referenced source file.
- Used the `content` table to look up the correct source file for each image.
- Patched `copy_images_to_build` to use this logic.
- Result: Images are now correctly copied to `build/images/`.

### 5. Validation & Directory Listing
- Ran `build-test.py` and confirmed images are present in `build/images/`.
- Used `ls -l build/images` to verify the copied images.

### 6. Remaining Issues
- Embedded images in notebooks and docx files (e.g., `notebook_embedded/...`, `docx_embedded/...`) still fail to copy, likely because the extraction logic is not implemented or the files do not exist.
- Remote images (URLs) are skipped by design.

---

## Lessons Learned
- Always resolve image paths relative to their source file, not the working directory.
- The `content` table is essential for robust path resolution.
- Validation via test harness and directory listing is critical for debugging.
- Remote and missing images should be logged and skipped gracefully.

---

## Next Steps
- Implement extraction logic for embedded notebook and docx images.
- Update markdown links to point to `images/<filename>` after copying.
- Continue to validate and document all changes in this file.

---

## Contributors
- GitHub Copilot (AI assistant)
- User: caballero

---

## Last Updated
July 14, 2025

---

# Implementation Notes for convert.py

## Purpose
This document provides implementation notes, design decisions, and usage tips for `convert.py`, the batch conversion and asset management script in OER Forge.

## Design Overview
- **TOC-Driven Conversion:** All files referenced in the Table of Contents (`_config.yml`) are copied to `build/files/`, preserving the hierarchy.
- **Image Handling:** All images referenced in content files are copied to a flat `build/images/` directory. Image references in markdown files are rewritten to use the format `../../images/<filename>`, ensuring correct links regardless of directory depth.
- **Database Integration:** Uses `sqlite.db` to track content, images, and conversion status. All image lookups and link rewrites are database-driven for robustness.
- **Format Conversion:** Markdown files can be converted to DOCX (implemented), PDF, and LaTeX (stubs) using Pandoc.
- **Logging:** All actions, errors, and warnings are logged for traceability.

## Implementation Highlights
- **Image Link Rewriting:**
  - All markdown image references are rewritten to use `../../images/<filename>`, regardless of the markdown file's location.
  - This is handled in `update_markdown_image_links`, which queries the database for image records and rewrites links accordingly.
- **Batch Conversion:**
  - The main function `batch_convert_all_content` walks the TOC, copies files, processes images, and updates markdown links.
  - Errors (missing files, failed copies, DB issues) are logged and do not halt the batch process.
- **Extensibility:**
  - Stubs for PDF and LaTeX conversion are present for future implementation.
  - The modular design allows for easy extension to other asset types or formats.

## Usage Tips
- Run the script directly to process all content:
  ```bash
  python oerforge/convert.py
  ```
- Check `build/files/` and `build/images/` for output. All image links in markdown should resolve correctly.
- Review logs in `log/` for errors and warnings.
- For documentation, see `content/docs/convert.md`.

## Troubleshooting
- If image links are incorrect, check the database for missing or misreferenced images.
- If files are missing from `build/files/`, verify the TOC in `_config.yml` and source files in `content/`.
- For conversion errors (DOCX, PDF, LaTeX), check Pandoc installation and log output.

## Change Log
- 2025-07-14: Image link rewriting standardized to `../../images/<filename>` for all markdown files.
- 2025-07-14: Documentation and implementation notes updated for batch conversion and asset extraction.

## Author
[Your Name]
