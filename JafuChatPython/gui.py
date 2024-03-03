import tkinter as tk
from tkinter import scrolledtext
from subprocess import Popen, PIPE
import os

# Relative paths
relative_python_exe_path = "venv/Scripts/python.exe"
relative_main_py_path = "main.py"

# Get absolute paths
absolute_python_exe_path = os.path.abspath(relative_python_exe_path)
absolute_main_py_path = os.path.abspath(relative_main_py_path)

class MainApplication(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.dir = "E:/docs/"
        self.cmd = absolute_python_exe_path + ' ' + absolute_main_py_path
        self.process = None

    def create_widgets(self):
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.config(font=("Times New Roman", 24))

        self.input_field = tk.Entry(self)
        self.input_field.pack(padx=10, fill=tk.X)
        self.input_field.config(font=("Times New Roman", 24))
        self.input_field.bind("<Return>", self.send_command)

        self.load_buttons()

    def load_buttons(self):
        files = [f for f in os.listdir(self.dir) if
                 os.path.isdir(os.path.join(self.dir, f)) and f.lower() != 'chatjafu']
        for file in files:
            button = tk.Button(self, text=file, command=lambda f=file: self.background_run(f))
            button.pack(pady=2)

    def background_run(self, directory):
        cmd = f"{self.cmd} {os.path.join(self.dir, directory)}"
        self.process = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        self.update_text_area()

    def send_command(self, event=None):
        command = self.input_field.get() + "\n"
        if self.process:
            self.process.stdin.write(command.encode())
            self.process.stdin.flush()
        self.input_field.delete(0, tk.END)

    def update_text_area(self):
        if self.process:
            for line in self.process.stdout:
                self.text_area.insert(tk.END, line.decode())
            self.text_area.yview(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("ChatJafu")
    app = MainApplication(root)
    app.mainloop()
