import os
from oerdocs.render_d2_diagrams import render_d2_to_png, SRC_DIR, IMG_DIR

def traverse_and_render():
    # Traverse the img directory (or any directory you want)
    for filename in os.listdir(SRC_DIR):
        if filename.endswith(".d2"):
            d2_path = os.path.join(SRC_DIR, filename)
            png_filename = os.path.splitext(filename)[0] + ".png"
            png_path = os.path.join(IMG_DIR, png_filename)
            print(f"Rendering {d2_path} -> {png_path}")
            try:
                render_d2_to_png(d2_path, png_path)
            except Exception as e:
                print(f"[ERROR] {e}")

if __name__ == "__main__":
    traverse_and_render()