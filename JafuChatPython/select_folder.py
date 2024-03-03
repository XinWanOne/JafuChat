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
