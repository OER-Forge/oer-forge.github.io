from oerforge.scan import initialize_database, insert_file_record, print_table, log_event, get_notebook_paths_from_toc


# Initialize the database (will drop and recreate tables)
initialize_database()

# Create a sample toc file with .ipynb entries
toc_path = 'sample_toc.txt'
with open(toc_path, 'w', encoding='utf-8') as f:
    f.write('notebook1.ipynb\n')
    f.write('notebook2.ipynb\n')
    f.write('README.md\n')
    f.write('# This is a comment\n')
    f.write('notebook3.ipynb\n')

# Test get_notebook_paths_from_toc
notebook_paths = get_notebook_paths_from_toc(toc_path)
print("Notebook paths found in TOC:", notebook_paths)

# Clean up sample toc file (optional)
import os
os.remove(toc_path)

