from oerforge.db_utils import initialize_database, insert_file_records, link_files_to_pages, pretty_print_table
from oerforge.scan import populate_site_info_from_config


# --- Modular DB function tests ---
def test_db_utils():
    print("[TEST] Initializing database...")
    initialize_database()

    print("[TEST] Testing site info scan...")
    config_path = '_config.yml'
    populate_site_info_from_config(config_path)
    print("[TEST] Printing 'site_info' table:")
    pretty_print_table('site_info')

    print("[TEST] Testing insert_file_records...")
    sample_files = [
        {
            'filename': 'test1.png',
            'extension': 'png',
            'mime_type': 'image/png',
            'is_image': 1,
            'is_remote': 0,
            'url': '',
            'referenced_page': 'about.md',
            'relative_path': 'assets/images/test1.png',
            'absolute_path': '/tmp/test1.png',
            'cell_type': None,
            'is_code_generated': None,
            'is_embedded': None
        },
        {
            'filename': 'test2.pdf',
            'extension': 'pdf',
            'mime_type': 'application/pdf',
            'is_image': 0,
            'is_remote': 1,
            'url': 'https://example.com/test2.pdf',
            'referenced_page': 'index.md',
            'relative_path': 'assets/docs/test2.pdf',
            'absolute_path': '/tmp/test2.pdf',
            'cell_type': None,
            'is_code_generated': None,
            'is_embedded': None
        }
    ]
    file_ids = insert_file_records(sample_files)
    print(f"Inserted file IDs: {file_ids}")

    print("[TEST] Testing link_files_to_pages...")
    file_page_pairs = [
        (file_ids[0], 'about.md'),
        (file_ids[1], 'index.md')
    ]
    link_files_to_pages(file_page_pairs)
    print("Linked files to pages.")

    print("[TEST] Printing 'files' table:")
    pretty_print_table('files')
    print("[TEST] Printing 'pages_files' table:")
    pretty_print_table('pages_files')


if __name__ == "__main__":
    test_db_utils()

