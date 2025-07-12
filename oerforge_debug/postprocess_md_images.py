import sys
import re

def postprocess_md_images(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    # Replace output_4_0.png → codeimg_4_0.png (preserving suffix)
    new_md_text = re.sub(r'output_([0-9_]+)\.png', r'codeimg_\1.png', md_text)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(new_md_text)
    print(f"[OK] Updated image references in {md_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python oerforge_debug/postprocess_md_images.py <markdown_file>")
        sys.exit(1)
    postprocess_md_images(sys.argv[1])