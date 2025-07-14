import yaml
import os
from oerforge.make import build_all_markdown_files, BUILD_FILES_DIR, BUILD_HTML_DIR

def test_build_files_and_html():
    with open("_config.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    toc = config.get("toc", [])

    def walk_toc_all_files(items):
        files = []
        for item in items:
            file_path = item.get("file")
            if file_path:
                files.append(file_path)
            children = item.get("children", [])
            if children:
                files.extend(walk_toc_all_files(children))
        return files

    all_files = walk_toc_all_files(toc)
    missing = []
    for file_path in all_files:
        build_path = os.path.join("build/files", file_path)
        if not os.path.exists(build_path):
            missing.append(build_path)
    if missing:
        print("[TEST][FAIL] Missing files in build/files:")
        for m in missing:
            print("  ", m)
    else:
        print("[TEST][PASS] All TOC-referenced files copied to build/files/ correctly.")
        print("[TEST] Building HTML from markdown in build/files...")
        build_all_markdown_files(BUILD_FILES_DIR, BUILD_HTML_DIR)
        print("[TEST][PASS] HTML build completed.")

if __name__ == "__main__":
    test_build_files_and_html()