__copyright__ = """

    Copyright 2024 Jason Hoford

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
__license__ = "Apache 2.0"

import os, shutil
import sys

import jafuGPT
from jafuGPT import run_private_gpt
from ingest import ingest_files

DB_DIR = "_db"


def main(folder_path):
    db = os.path.join(folder_path, DB_DIR)
    if not os.path.exists(db):
        ingest_files(folder_path, db)
    print()
    print("Welcome to Chat With Jafu!")
    print(f"Using LLM model: {jafuGPT.model}.")
    print(f"Answering questions about contents in \"{folder_path}\".")
    print("Type \"quit\" to exit.")
    print("\nEnter a query: ")
    run_private_gpt(folder_path, db)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [-r] <folder_path>")
    index = 1
    if "-llm" == sys.argv[index]:
        index = index + 1
        jafuGPT.LLM_MODEL = sys.argv[index]
        index = index + 1
        jafuGPT.model = os.environ.get("MODEL", jafuGPT.LLM_MODEL)
        print("using model", jafuGPT.model)

    if "-r" == sys.argv[index]:
        index = index + 1
        shutil.rmtree(os.path.join(sys.argv[index], DB_DIR))
    folder_path = sys.argv[index]
    if not os.path.isdir(folder_path):
        print("Error: Provided path is not a folder.")
    print(">>> " + folder_path)
    main(folder_path)
