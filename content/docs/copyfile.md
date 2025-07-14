# oerforge/copyfile.py

## Overview

`copyfile.py` is a utility module for copying project content and static assets into build directories for deployment. It is designed to prepare all necessary files for static site generation and publishing, including support for GitHub Pages.

## Features
- **Copies all contents of `content/` to `build/files/`**: Ensures all source content is available in the build output.
- **Copies `static/css/` to `build/css/` and `static/js/` to `build/js/`**: Makes sure all CSS and JS assets are present for the site to function and look correct.
- **Creates target directories if they do not exist**: Robust against missing folders.
- **Overwrites files each time it is called**: Ensures a clean build output.
- **Creates `build/.nojekyll`**: Prevents GitHub Pages from running Jekyll, allowing full access to files and folders.

## Usage
```python
from oerforge.copyfile import copy_project_files
copy_project_files()
```

## Functions

### copytree_overwrite(src, dst)
Recursively copies the contents of the source directory `src` to the destination directory `dst`, overwriting any existing files or folders at the destination. If the destination exists, it is removed before copying.
- **Parameters:**
  - `src` (str): Source directory path.
  - `dst` (str): Destination directory path.
- **Logging:**
  - Logs debug messages for copying and removal actions.

### ensure_dir(path)
Ensures that the directory at `path` exists. If it does not, it is created.
- **Parameters:**
  - `path` (str): Directory path to ensure.
- **Logging:**
  - Logs debug messages when creating directories.

### create_nojekyll(path)
Creates an empty `.nojekyll` file at the specified path. This is required for GitHub Pages to serve files and folders as-is, without Jekyll processing.
- **Parameters:**
  - `path` (str): Path to the `.nojekyll` file.
- **Logging:**
  - Logs info messages when the file is created.

### copy_project_files(debug: bool = False)
Main entry point for copying all project content and static assets to the build directory. This function:
- Sets up logging (debug or info level).
- Removes the entire build directory if it exists (destructive, ensures a clean build).
- Ensures the build directory exists.
- Copies content, CSS, and JS assets to their respective build locations.
- Creates the `.nojekyll` file.
- **Parameters:**
  - `debug` (bool): If True, enables detailed debug logging.
- **Logging:**
  - Logs all major actions and errors to `log/build.log`.

## Example Workflow
1. **Remove old build output:**
   - Deletes the entire `build/` directory if present.
2. **Create build directory:**
   - Ensures `build/` exists.
3. **Copy content:**
   - Copies everything from `content/` to `build/files/`.
4. **Copy CSS and JS:**
   - Copies everything from `static/css/` to `build/css/`.
   - Copies everything from `static/js/` to `build/js/`.
5. **Create .nojekyll:**
   - Creates an empty file at `build/.nojekyll`.
6. **Logging:**
   - All actions are logged to `log/build.log` for traceability.

## Notes
- This module is destructive: it removes the entire build directory before copying.
- It is intended to be called as part of a build pipeline before HTML conversion and deployment.
- The logging setup ensures that all actions are traceable for debugging and auditing purposes.

## Best Practices
- Always call `copy_project_files()` before running conversion or build steps to ensure a clean and complete build output.
- Use the `debug=True` option during development to get detailed logs.
- Check `log/build.log` for any issues or errors during the copy process.

## Example
```python
from oerforge.copyfile import copy_project_files
copy_project_files(debug=True)
```

This will copy all content and static assets, overwrite the build directory, and log detailed actions.
