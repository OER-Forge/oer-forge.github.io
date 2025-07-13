import os

def test_relpath():
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filename='test_paths.log', filemode='w')
    print("[TEST] os.path.relpath computation for menu links")
    cases = [
        # (current_html_path, target_html)
        ("build/index.html", "build/index.html"),
        ("build/docs/index.html", "build/index.html"),
        ("build/docs/index.html", "build/docs/index.html"),
        ("build/docs/index.html", "build/dev/index.html"),
        ("build/docs/subsection/page.html", "build/index.html"),
        ("build/docs/subsection/page.html", "build/docs/index.html"),
        ("build/docs/subsection/page.html", "build/docs/subsection/page.html"),
        ("build/docs/subsection/page.html", "build/dev/index.html"),
        ("build/dev/index.html", "build/docs/index.html"),
        ("build/dev/index.html", "build/dev/index.html"),
    ]
    for current_html, target_html in cases:
        current_dir = os.path.dirname(current_html)
        try:
            rel = os.path.relpath(target_html, start=current_dir)
            debug_msg = f"[DEBUG] From: {current_html} (dir: {current_dir}) -> To: {target_html} => relpath: {rel}"
            print(debug_msg)
            logging.debug(debug_msg)
        except Exception as e:
            error_msg = f"[DEBUG] relpath error: {e} for case: current_html={current_html}, target_html={target_html}"
            print(error_msg)
            logging.error(error_msg)

if __name__ == "__main__":
    test_relpath()
