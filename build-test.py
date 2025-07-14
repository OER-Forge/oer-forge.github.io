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

