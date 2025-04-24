
import tkinter as tk
from tkinter import simpledialog

class EditPopup(tk.Toplevel):
    def __init__(self, master, filename, old_content, on_save):
        super().__init__(master)
        self.title(f"Sửa nội dung - {filename}")
        self.geometry("500x300")
        self.resizable(False, False)
        self.on_save = on_save

        tk.Label(self, text="Tên file:").pack(anchor='w', padx=10, pady=(10, 0))
        tk.Label(self, text=filename, fg="blue").pack(anchor='w', padx=10)

        tk.Label(self, text="Nội dung:").pack(anchor='w', padx=10, pady=(10, 0))
        self.textbox = tk.Text(self, wrap='word', height=10)
        self.textbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.textbox.insert('1.0', old_content)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Hủy", command=self.destroy).pack(side='right', padx=10)
        tk.Button(btn_frame, text="Lưu", command=self.save).pack(side='right')

    def save(self):
        new_content = self.textbox.get('1.0', 'end').strip()
        self.on_save(new_content)
        self.destroy()
