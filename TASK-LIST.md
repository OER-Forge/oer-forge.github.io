# Task List

## 1. **config_parser.py**

### Writing
- **Step 1:** Import `yaml` and set up basic file reading.
- **Step 2:** Write `parse_config(config_path: str) -> dict` to:
  - Open and read the YAML file.
  - Parse YAML to a Python dict.
  - Validate required top-level keys (`site`, `toc`, `footer`, static, `build`).
  - Validate types (e.g., `toc` is a list, `site` is a dict).
  - Raise exceptions and log errors for missing/invalid fields.
- **Step 3:** Add docstrings and type hints.

### Testing
- **Step 1:** Create test configs:
  - Valid config.
  - Missing required keys.
  - Wrong types (e.g., `toc` as a string).
  - Malformed YAML.
- **Step 2:** Write a test script or use `pytest` to:
  - Load each config and check for correct parsing or error handling.
  - Assert that exceptions are raised for invalid configs.
- **Step 3:** Test with large and deeply nested configs.

### Debugging Edge Cases
- Malformed YAML (catch `yaml.YAMLError`).
- Extra/unexpected keys (warn, but don’t fail).
- Unicode and encoding issues.
- Empty config file.
- Duplicate keys in YAML.

---

## 2. **toc_extractor.py**

### Writing
- **Step 1:** Accept parsed config dict.
- **Step 2:** Traverse `toc` recursively:
  - Handle nested `children` and `file` keys.
  - Build a structured list or tree (e.g., for menus/pages).
- **Step 3:** Provide functions to:
  - Return a flat list of all files.
  - Return a nested menu structure.
  - Validate that all referenced files exist.
- **Step 4:** Add docstrings and type hints.

### Testing
- **Step 1:** Use sample configs with:
  - Simple TOC (one level).
  - Deeply nested TOC.
  - TOC with missing `file` or `children`.
  - TOC with circular references (should warn or fail).
- **Step 2:** Write tests to:
  - Check correct extraction of menu/page structure.
  - Assert correct handling of missing or malformed entries.
- **Step 3:** Test with TOC referencing non-existent files.

### Debugging Edge Cases
- Missing `file` or `children` keys.
- Circular references in TOC.
- Duplicate titles or file paths.
- Empty TOC.
- Non-list TOC (e.g., dict or string).

---

## 3. **content_converter.py**

### Writing
- **Step 1:** Set up conversion functions for each format:
  - Markdown: Use `markdown`, `pandoc`, or similar.
  - Docx: Use `python-docx`, `pandoc`.
  - ipynb: Use `nbconvert`, `pandoc`.
- **Step 2:** Write `convert_content(file_path, output_formats, config)` to:
  - Detect file type.
  - Call appropriate conversion function.
  - Avoid redundant conversions (check if output exists and is up-to-date).
  - Preserve figures and media (copy images, update links).
  - Log status and errors.
- **Step 3:** Add docstrings and type hints.

### Testing
- **Step 1:** Prepare sample files for each format.
- **Step 2:** Write tests to:
  - Convert each file to all supported formats.
  - Check output files for correctness (content, images, formatting).
  - Test with files containing images, tables, code blocks, math.
- **Step 3:** Test conversion with large files and files with edge-case content (e.g., broken links, unsupported features).

### Debugging Edge Cases
- Unsupported file types (should log and skip).
- Conversion failures (catch exceptions, log errors).
- Missing images or media (warn, use placeholder).
- Files with special characters, Unicode, or non-UTF8 encoding.
- Output directory not writable or missing.
