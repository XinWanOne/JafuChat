import tkinter as tk
from tkinter import filedialog
import json
import sys
import platform
import os

def open_folder():
    root = tk.Tk()
    top = tk.Toplevel(root)
    top.attributes('-topmost', True)
    top.withdraw()
    parent = top if platform.system() == "Windows" else None
    initial_dir = ''
    arguments = sys.argv[1:]
    if len(arguments) > 0:
        initial_dir = arguments[0]
    folder_path = filedialog.askdirectory(parent=parent, initialdir=initial_dir)
    top.destroy()
    root.destroy()
    if not folder_path:
        return False
    return folder_path

# Load the existing JSON file

json_file_path = "data.json"
def change_folder_path_with_dp_change():
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
    selected_folder = open_folder()
    if selected_folder:
        folder_path, folder_name = os.path.split(selected_folder)
        data['FOLDER_PATH'] = selected_folder
        data['base_data'] = folder_name
        data['base_data_store'] = folder_path
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        return True
    else:
        return False


if __name__ == '__main__':
    selected_folder = open_folder()
    print("Selected folder:", selected_folder)