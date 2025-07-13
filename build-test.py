from oerforge.scan import initialize_database, insert_file_record, print_table

# Initialize the database (will drop and recreate tables)
initialize_database()

# Insert a sample file record with new notebook asset fields
sample_file_record = {
    'filename': 'test_image.png',
    'extension': 'png',
    'mime_type': 'image/png',
    'is_image': 1,
    'is_remote': 0,
    'url': '',
    'referenced_page': 'notebook1.ipynb',
    'relative_path': 'images/test_image.png',
    'absolute_path': '/abs/path/to/images/test_image.png',
    'cell_type': 'code',
    'is_code_generated': 1,
    'is_embedded': 0
}
insert_file_record(sample_file_record)

# Print the files table to verify new fields
print_table('files')

