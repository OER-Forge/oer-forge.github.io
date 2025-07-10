import re
import sys
import json
from pathlib import Path

def remove_remote_images_from_md(md_content, debug=False):
    pattern = r'!\[[^\]]*\]\((http[^\)]+)\)'
    warning = '\n> **[Image not embedded: remote images are not included in PDF export. Check the original file for the image.]**\n'
    def repl(match):
        if debug:
            print(f"[DEBUG] Removing remote image: {match.group(0)}")
        return warning
    return re.sub(pattern, repl, md_content)

def process_md_file(input_path, output_path, debug=False):
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    new_content = remove_remote_images_from_md(md_content, debug=debug)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    if debug:
        print(f"[DEBUG] Processed Markdown: {input_path} -> {output_path}")

def process_ipynb_file(input_path, output_path, debug=False):
    with open(input_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    changed = False
    for idx, cell in enumerate(nb.get('cells', [])):
        if cell.get('cell_type') == 'markdown':
            src = cell.get('source', [])
            if isinstance(src, list):
                src_str = ''.join(src)
            else:
                src_str = src
            new_src = remove_remote_images_from_md(src_str, debug=debug)
            if new_src != src_str:
                changed = True
                if isinstance(src, list):
                    cell['source'] = [line for line in new_src.splitlines(keepends=True)]
                else:
                    cell['source'] = new_src
                if debug:
                    print(f"[DEBUG] Removed remote images from notebook cell {idx+1}")
    if changed:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        if debug:
            print(f"[DEBUG] Processed Notebook: {input_path} -> {output_path}")
    else:
        if debug:
            print(f"[DEBUG] No remote images found in: {input_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Remove remote images from Markdown and Notebook files.")
    parser.add_argument('--files', nargs='+', required=True, help='Files to process (.md or .ipynb)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()

    for file in args.files:
        input_path = Path(file)
        if not input_path.exists():
            print(f"[ERROR] File not found: {file}")
            continue
        output_path = input_path.parent / (input_path.stem + "_no_remote" + input_path.suffix)
        if input_path.suffix.lower() == '.md':
            process_md_file(input_path, output_path, debug=args.debug)
        elif input_path.suffix.lower() == '.ipynb':
            process_ipynb_file(input_path, output_path, debug=args.debug)
        else:
            print(f"[SKIP] Unsupported file type: {file}")

if __name__ == "__main__":
    main()