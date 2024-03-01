import os, shutil
import sys

from ingest import ingest_files
from main import DB_DIR

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python",sys.argv[0],"<folder_path>")
        sys.exit()
    index = 1
    folder_path = sys.argv[index]
    if not os.path.isdir(folder_path):
        print("Error: Provided path is not a folder.")
        sys.exit()
    db = os.path.join(folder_path, DB_DIR)
    if os.path.isdir(db):
        shutil.rmtree(db)

    print(">>> "+folder_path)
    ingest_files(folder_path, db)
