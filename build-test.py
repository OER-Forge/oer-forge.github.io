from oerforge.db_utils import initialize_database
from oerforge.scan import batch_read_files


# --- Batch file reading test ---
def test_batch_read_files():
    print("[TEST] Initializing database...")
    initialize_database()

    # Use markdown, notebook, and docx files for the test
    file_paths = [
        "content/about.md",
        "content/sample/notebooks/01_notes.ipynb",
        "content/sample/activity-metropolis.docx",
        "content/sample/notes-phase_space.docx"
    ]
    print(f"[TEST] Reading files: {file_paths}")
    contents = batch_read_files(file_paths)
    for path, content in contents.items():
        print(f"\n[CONTENTS of {path}]:\n{content}\n")


if __name__ == "__main__":
    test_batch_read_files()

    # --- Batch asset extraction test ---
    from oerforge.scan import batch_extract_assets

    file_paths = [
        "content/about.md",
        "content/sample/notebooks/01_notes.ipynb",
        "content/sample/activity-metropolis.docx",
        "content/sample/notes-phase_space.docx",
        "content/sample/notebooks/02_notes.ipynb",
        "content/sample/notebooks/07_notes.ipynb"
    ]
    contents = batch_read_files(file_paths)


    # Batch asset extraction and DB population for all file types
    from oerforge.scan import batch_extract_assets

    # Markdown
    md_files = [p for p in file_paths if p.endswith('.md')]
    md_contents = {p: contents[p] for p in md_files}
    md_assets = batch_extract_assets(md_contents, 'markdown')
    print("\n[ASSETS extracted from markdown files]:")
    for path, assets in md_assets.items():
        print(f"{path}: {assets}")

    # Notebook
    nb_files = [p for p in file_paths if p.endswith('.ipynb')]
    nb_contents = {p: contents[p] for p in nb_files}
    nb_assets = batch_extract_assets(nb_contents, 'notebook')
    print("\n[ASSETS extracted from notebook files]:")
    for path, assets in nb_assets.items():
        print(f"{path}: {assets}")

    # Docx
    docx_files = [p for p in file_paths if p.endswith('.docx')]
    docx_contents = {p: contents[p] for p in docx_files}
    docx_assets = batch_extract_assets(docx_contents, 'docx')
    print("\n[ASSETS extracted from docx files]:")
    for path, assets in docx_assets.items():
        print(f"{path}: {assets}")

    # Print DB tables after all asset extraction and DB population
    from oerforge.db_utils import pretty_print_table
    print("\n[DB TABLE: files]")
    pretty_print_table('files')
    print("\n[DB TABLE: pages]")
    pretty_print_table('pages')
    print("\n[DB TABLE: pages_files]")
    pretty_print_table('pages_files')
    print("\n[DB TABLE: site_info]")
    pretty_print_table('site_info')

    # --- Export DB tables to HTML admin pages ---
    print("\n[TEST] Exporting DB tables to HTML admin pages...")
    from oerforge_admin.export_db_html import export_all_tables_to_html, copy_static_assets_to_admin
    admin_output_dir = "build/admin/"
    export_all_tables_to_html(admin_output_dir)
    copy_static_assets_to_admin(admin_output_dir)
    print(f"[TEST] Admin HTML pages generated in {admin_output_dir}")

