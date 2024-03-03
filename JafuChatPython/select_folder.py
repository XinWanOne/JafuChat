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

import platform
import sys

import tkinter as tk
from tkinter import filedialog
import os
from configuration import configure, initial_setup, set_selected_folder


# using TK for now
def open_folder():
    """
    Gets the folder path by creating an explore window
    """
    root = tk.Tk()
    top = tk.Toplevel(root)
    top.attributes('-topmost', True)
    top.withdraw()
    parent = top if platform.system() == "Windows" else None
    initial_dir = ''
    arguments = sys.argv[1:]
    if len(arguments) > 0:
        initial_dir = arguments[0]
    folder_path = filedialog.askopenfilename(parent=parent, initialdir=initial_dir)
    top.destroy()
    root.destroy()
    if not folder_path:
        return False

# Load the existing JSON file
# json_file_path = "data.json"
# Check if the selected path is a folder
    if os.path.isdir(folder_path):
        return folder_path
    else:
        return False



def change_folder_path_with_dp_change():
    # with open(json_file_path, "r") as json_file:
    #     data = json.load(json_file)
    # data = {}
    folder = open_folder()
    if folder:
        set_selected_folder(folder)
        return True
    else:
        return False


def initial_setup_with_select():
    if configure():
        return
    db_folder = open_folder()
    initial_setup(db_folder)


if __name__ == '__main__':
    selected_folder = open_folder()
    print("Selected folder:", selected_folder)
