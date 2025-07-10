# Task List

## Project Description

This document outlines the step-by-step development plan for the core modules of the OER Forge site builder. The goal is to create a robust, modular Python system that can parse configuration files, extract and organize the table of contents, and convert educational content into multiple formats for web publishing. Each module is designed for clarity, testability, and extensibility, with careful attention to edge cases and error handling. The first three modules are:

1. **config_parser.py**: Responsible for reading and validating the main YAML configuration file (`_config.yml`). It ensures all required fields are present and correctly typed, and provides a clean Python object for downstream processing. This module is the foundation for all site logic and must be resilient to malformed or incomplete configs.

2. **toc_extractor.py**: Traverses the parsed configuration to extract the table of contents (TOC), building a structured representation of the site's navigation and content hierarchy. It supports nested chapters, validates file references, and helps generate menus and page lists for the site. Robust handling of missing, circular, or malformed TOC entries is essential.

3. **content_converter.py**: Converts source files (Markdown, DOCX, Jupyter Notebooks) into multiple output formats (HTML, PDF, DOCX, TEX, etc.), preserving figures and media. It avoids redundant conversions, logs status and errors, and gracefully handles unsupported or problematic files. This module is key for generating accessible, multi-format educational resources.

The plan below details the writing, testing, and debugging process for each module, ensuring that each step is actionable and verifiable. Edge cases and error conditions are explicitly considered to maximize reliability and maintainability.

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


# Build Notes

## 1. **Set Up Your Development Environment**
- Install Python 3.9+ and create a virtual environment.
- Install required packages (e.g., `PyYAML`, `markdown`, `nbformat`, `nbconvert`, `python-docx`, `pdfkit`, etc.).
- Make sure your directory structure matches the scaffold.

## 2. **Build and Test the Config Parser**
- Implement config_parser.py:
  - Parse _config.yml and validate its structure.
  - Return a Python dictionary or custom object.
  - Log errors for missing/invalid fields.
- **Test:** Write a simple script to load and print the config. Try with valid and invalid configs.

## 3. **Extract and Test the Table of Contents**
- Implement toc_extractor.py:
  - Accept the parsed config.
  - Traverse the TOC and return a structured menu/page list.
  - Handle nested chapters and children.
- **Test:** Print the extracted TOC structure. Check for correct nesting and file paths.

## 4. **Build and Test Content Converters**
- Implement content_converter.py:
  - For markdown: Convert to HTML, PDF, DOCX, TEX.
  - For docx: Convert to markdown, HTML, PDF.
  - For ipynb: Convert to HTML, PDF, TEX, and copy as-is.
  - Use libraries and avoid redundant conversions.
  - Preserve figures and media.
- **Test:** Run conversions on sample files. Check output formats and figure preservation.

## 5. **Handle Remote Images**
- Implement image_manager.py:
  - Scan files for remote image URLs.
  - Download images with `curl`.
  - Replace missing images with a placeholder and URL.
  - Organize images in static directories.
- **Test:** Use files with remote images (including GIFs and broken links). Verify downloads and replacements.

## 6. **Inject Accessibility Features**
- Implement accessibility.py:
  - Add buttons for download, text size, and spacing adjustments to HTML.
  - Ensure WCAG compliance.
- **Test:** Open generated HTML and verify accessibility features.

## 7. **Organize Output Files**
- Implement output_manager.py:
  - Move/copy converted files to `_build/` and `docs/` by format.
  - Ensure correct folder structure.
- **Test:** Check that files are in the right places after conversion.

## 8. **Build Jupyterbook from Notebooks**
- Implement jupyterbook_builder.py:
  - Accept notebook paths and output directory.
  - Use `nbconvert` or `jupyter-book` CLI to compile.
  - Build HTML pages for notebooks.
- **Test:** Compile a set of notebooks and verify the jupyterbook output.

## 9. **Implement Logging and Progress Tracking**
- Implement logger.py:
  - Print `[OK]`, `[WARN]`, `[ERROR]`, `[DEBUG]` messages.
  - Only print `[DEBUG]` if enabled.
- Implement progress.py:
  - Track and print percent completion.
  - Print a summary of results at the end.
- **Test:** Run a build and verify logging and progress output.

## 10. **Build Utility Functions**
- Implement utils.py:
  - Add reusable helpers for file I/O, string manipulation, etc.
- **Test:** Use utilities in other modules and verify correctness.

## 11. **Orchestrate the Build Process**
- Implement build.py:
  - Parse command-line arguments (`--pdf`, `--tex`, `--html`, `--files`, `--debug`).
  - Call appropriate modules/functions based on flags.
  - Print progress and summary.
  - Log all actions and errors.
- **Test:** Run builds with different flags and file selections. Check outputs and logs.

## 12. **Integrate and Test End-to-End**
- Run the full build process on a subset of your content.
- Validate that all outputs are correct, accessible, and organized.
- Check that figures, images, and navigation work as expected.

## 13. **Iterate and Refine**
- Add more tests and edge cases.
- Refactor for performance and maintainability.
- Document all modules and functions.

## Directory and Code Stubs

Here is a detailed view of your oerforge directory and the stub code in each Python module, outlining the plan and responsibilities for each part of your site builder:

---

### Directory Listing (`ls -lR oerforge/`)
```
.rw-r--r--   -- __init__.py
.rw-r--r--   -- accessibility.py
.rw-r--r--   -- config_parser.py
.rw-r--r--   -- content_converter.py
.rw-r--r--   -- image_manager.py
.rw-r--r--   -- jupyterbook_builder.py
.rw-r--r--   -- logger.py
.rw-r--r--   -- output_manager.py
.rw-r--r--   -- progress.py
.rw-r--r--   -- toc_extractor.py
.rw-r--r--   -- utils.py
```

---

### Python Stub Contents

#### config_parser.py
```python
"""
Module: config_parser

Purpose: Parses and validates _config.yml for site, TOC, footer, static, and build options. This module should:
- Read the YAML config file.
- Validate required fields and structure.
- Return a Python dictionary or custom object for use by other modules.
- Raise exceptions and log errors if config is invalid.
- Use type hints and clear docstrings for all functions.
"""
def parse_config(config_path: str) -> dict:
    """Parse and validate the config file.
    Args:
        config_path: Path to _config.yml
    Returns:
        Parsed config as a dictionary.
    """
    pass
```

#### toc_extractor.py
```python
"""
Module: toc_extractor

Purpose: Extracts and organizes the table of contents from the config. This module should:
- Accept the parsed config object.
- Traverse the TOC structure and return a menu/page structure.
- Provide functions to generate navigation menus for the site.
- Use type hints and clear docstrings for all functions.
"""
def extract_toc(config: dict) -> list:
    """Extract TOC structure from config.
    Args:
        config: Parsed config dictionary.
    Returns:
        List representing the TOC structure.
    """
    pass
```

#### content_converter.py
```python
"""
Module: content_converter

Purpose: Converts markdown, docx, and ipynb files to required formats. This module should:
- Accept file paths and output format list.
- Use appropriate libraries for conversion.
- Avoid redundant conversions.
- Preserve figures and media.
- Log status and errors.
- Use type hints and clear docstrings for all functions.
"""
def convert_content(file_path: str, output_formats: list, config: dict) -> None:
    """Convert content file to specified formats.
    Args:
        file_path: Path to input file.
        output_formats: List of formats to convert to.
        config: Parsed config dictionary.
    """
    pass
```

#### accessibility.py
```python
"""
Module: accessibility

Purpose: Injects accessibility features into HTML pages. This module should:
- Add buttons for download, text size, and spacing adjustments.
- Ensure WCAG compliance.
- Provide reusable functions for HTML injection.
- Use type hints and clear docstrings for all functions.
"""
def inject_accessibility(html_path: str) -> None:
    """Inject accessibility features into HTML.
    Args:
        html_path: Path to HTML file.
    """
    pass
```

#### image_manager.py
```python
"""
Module: image_manager

Purpose: Handles downloading and replacing remote images. This module should:
- Scan content files for remote images.
- Download images using curl.
- Replace missing images with a placeholder and URL.
- Organize figures in static directories.
- Use type hints and clear docstrings for all functions.
"""
def manage_images(file_path: str, static_dir: str) -> None:
    """Download remote images and handle missing images.
    Args:
        file_path: Path to content file.
        static_dir: Directory for static images.
    """
    pass
```

#### output_manager.py
```python
"""
Module: output_manager

Purpose: Organizes output files into build and docs directories. This module should:
- Move/copy files to _build/ and docs/ by format.
- Ensure correct folder structure.
- Log actions and errors.
- Use type hints and clear docstrings for all functions.
"""
def organize_output(src_path: str, dest_dir: str, format: str) -> None:
    """Move/copy files to output directories.
    Args:
        src_path: Source file path.
        dest_dir: Destination directory.
        format: File format.
    """
    pass
```

#### jupyterbook_builder.py
```python
"""
Module: jupyterbook_builder

Purpose: Compiles notebooks into a jupyterbook and builds HTML. This module should:
- Accept a list of notebook paths and output directory.
- Use nbconvert or jupyter-book CLI for compilation.
- Log status and errors.
- Use type hints and clear docstrings for all functions.
"""
def build_jupyterbook(notebook_paths: list, output_dir: str) -> None:
    """Build jupyterbook from notebooks.
    Args:
        notebook_paths: List of notebook file paths.
        output_dir: Output directory for jupyterbook.
    """
    pass
```

#### logger.py
```python
"""
Module: logger

Purpose: Provides logging functions for status messages. This module should:
- Print [OK], [WARN], [ERROR], [DEBUG] messages.
- Only print [DEBUG] if enabled.
- Use type hints and clear docstrings for all functions.
"""
def log(message: str, level: str = "INFO") -> None:
    """Log a message with a given level.
    Args:
        message: Message to log.
        level: Log level (OK, WARN, ERROR, DEBUG).
    """
    pass
```

#### progress.py
```python
"""
Module: progress

Purpose: Tracks and prints percent completion and summary. This module should:
- Update and print progress as tasks complete.
- Print a summary of results at the end.
- Use type hints and clear docstrings for all functions.
"""
def update_progress(current: int, total: int) -> None:
    """Update and print progress.
    Args:
        current: Current progress count.
        total: Total count.
    """
    pass

def print_summary(results: dict) -> None:
    """Print summary of build results.
    Args:
        results: Dictionary of results.
    """
    pass
```

#### utils.py
```python
"""
Module: utils

Purpose: Shared utility functions for file I/O and string manipulation. This module should:
- Provide reusable helpers for other modules.
- Use type hints and clear docstrings for all functions.
"""
def read_file(file_path: str) -> str:
    """Read file contents.
    Args:
        file_path: Path to file.
    Returns:
        File contents as string.
    """
    pass
```

#### build.py
```python
"""
Main build orchestration script.

Purpose: Handles command-line flags and calls modules to build the site. This script should:
- Parse command-line arguments (e.g., --pdf, --tex, --html, --files, --debug).
- Orchestrate the build process using the modules above.
- Print progress and summary.
- Log all actions and errors.
- Use type hints and clear docstrings for all functions.
"""
def main():
    """Main entry point for build orchestration."""
    pass

if __name__ == "__main__":
    main()
```