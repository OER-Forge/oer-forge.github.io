"""
render_d2_diagrams.py

This script scans the src/ directory for D2 diagram files (*.d2) and renders each as a PNG image in the img/ directory using the D2 CLI tool.

Requirements:
    - D2 CLI must be installed and available in your system PATH.
      Install with: brew install d2 (macOS) or see https://d2lang.com for other platforms.

Usage:
    python documentation/render_d2_diagrams.py
    # PNGs will be saved in img/ with the same base filename as the .d2 file.

Directory Structure:
    src/   - contains .d2 files (input diagrams)
    img/   - will contain .png files (output diagrams)
"""

import os
import subprocess

SRC_DIR = os.path.join(os.path.dirname(__file__), "../src")
IMG_DIR = os.path.join(os.path.dirname(__file__), "../img")

# Ensure output directory exists
os.makedirs(IMG_DIR, exist_ok=True)

def render_d2_to_png(d2_path, png_path):
    """
    Render a D2 diagram file to PNG using the D2 CLI tool.

    Args:
        d2_path (str): Path to the input .d2 file.
        png_path (str): Path to the output .png file.

    Raises:
        subprocess.CalledProcessError: If the D2 CLI fails.
    """
    print(f"[INFO] Running: d2 {d2_path} {png_path}")
    subprocess.run(["d2", d2_path, png_path], check=True)

def main():
    """
    Scan SRC_DIR for .d2 files and render each to PNG in IMG_DIR.
    """
    for filename in os.listdir(SRC_DIR):
        if filename.endswith(".d2"):
            d2_path = os.path.join(SRC_DIR, filename)
            png_filename = os.path.splitext(filename)[0] + ".png"
            png_path = os.path.join(IMG_DIR, png_filename)
            print(f"Rendering {d2_path} -> {png_path}")
            try:
                render_d2_to_png(d2_path, png_path)
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to render {d2_path}: {e}")

if __name__ == "__main__":
    main()