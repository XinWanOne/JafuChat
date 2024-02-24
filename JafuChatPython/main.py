import os, shutil
import sys

import jafuGPT
from jafuGPT import run_privateGPT
from ingest import ingest_files as ingest

DB_DIR = "_db"

def main(folder_path):
    db = os.path.join(folder_path, DB_DIR)
    if not os.path.exists(db):
        ingest(folder_path,db)
    print()
    print("Welcome to Chat With Jafu!")
    print(f"Using LLM model: {jafuGPT.model}.")
    print(f"Answering questions about contents in \"{folder_path}\".")
    print("Type \"quit\" to exit.")
    run_privateGPT(folder_path,db)

"""r('<urllib3.connection.HTTPConnection object at 0x000001F76ECA6390>: Failed to establish a new connection: [
WinError 10061] No connection could be made because the target machine actively refused it'))

"""
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [-r] <folder_path>")
    folder_path = sys.argv[1]
    if "-r" == sys.argv[1]:
        shutil.rmtree(os.path.join(sys.argv[2], DB_DIR))
        folder_path = sys.argv[2]

    if not os.path.isdir(folder_path):
        print("Error: Provided path is not a folder.")

    main(folder_path)
