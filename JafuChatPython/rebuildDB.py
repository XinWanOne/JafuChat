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

from ingest import ingest_files
from main import DB_DIR

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python", sys.argv[0], "<folder_path>")
        sys.exit()
    index = 1
    folder_path = sys.argv[index]
    if not os.path.isdir(folder_path):
        print("Error: Provided path is not a folder.")
        sys.exit()
    db = os.path.join(folder_path, DB_DIR)
    if os.path.isdir(db):
        shutil.rmtree(db)

    print(">>> " + folder_path)
    ingest_files(folder_path, db)
