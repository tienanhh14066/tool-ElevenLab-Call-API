import os, threading, requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from Core import core_logic

API_KEY = 'YOUR_ELEVENLABS_API_KEY'
VOICE_ID = 'EXAVITQu4vr4xnSDxMaL'  # thay ID nếu muốn giọng khác
URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

HEADERS = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

loaded_data = []

class StatusTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý trạng thái file txt")

        self.select_btn = tk.Button(root, text="Chọn thư mục", command=self.select_folder)
        self.select_btn.pack(pady=5)

        self.run_btn = tk.Button(root, text="🔊 Chạy TTS", command=self.run_tts)
        self.run_btn.pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("STT", "Tên txt", "Nội Dung", "Trạng Thái", "Ghi Chú", "Chạy Lại"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', self.edit_cell)

        style = ttk.Style()
        style.configure("Treeview", rowheight=28)
        style.map("Treeview", background=[('selected', '#ececec')])

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            global loaded_data
            loaded_data = core_logic.get_txt_files(folder)
            self.populate_table()

    def populate_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in loaded_data:
            values = [row[col] for col in self.tree["columns"][:-1]]
            item_id = self.tree.insert("", "end", values=values)
            self.colorize_row(item_id, row["Trạng Thái"])
            if row["Trạng Thái"] == "Thất Bại":
                self.tree.set(item_id, "Chạy Lại", "[Nút]")

    def colorize_row(self, item_id, status):
        color_map = {
            "Chờ": "#fffccc",
            "Thành Công": "#ccffcc",
            "Thất Bại": "#ffcccc",
            "đang xử lý": "#d0e0ff"
        }
        self.tree.item(item_id, tags=(status,))
        self.tree.tag_configure(status, background=color_map.get(status, "white"))

    def edit_cell(self, event):
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        col_index = int(col.replace('#', '')) - 1
        col_name = self.tree["columns"][col_index]
        if col_name != "Nội Dung":
            return
        current_status = self.tree.set(item_id, "Trạng Thái")
        if current_status not in ["Chờ", "Thất Bại"]:
            return
        old_value = self.tree.set(item_id, col_name)
        entry = tk.Entry(self.root)
        entry.insert(0, old_value)
        def save_edit(event):
            new_value = entry.get()
            self.tree.set(item_id, col_name, new_value)
            entry.destroy()
            index = int(self.tree.set(item_id, "STT")) - 1
            loaded_data[index]["Nội Dung"] = new_value
            core_logic.update_txt_file(loaded_data[index]["Path"], new_value)
            messagebox.showinfo("Lưu thành công", f"Đã lưu thay đổi cho {loaded_data[index]['Tên txt']}.")
        bbox = self.tree.bbox(item_id, col)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        entry.focus()
        entry.bind('<Return>', save_edit)

    def run_tts(self):
        threading.Thread(target=self.process_all, daemon=True).start()

    def process_all(self):
        for i, row in enumerate(loaded_data):
            self.tree.set(self.tree.get_children()[i], "Trạng Thái", "đang xử lý")
            self.colorize_row(self.tree.get_children()[i], "đang xử lý")
            try:
                payload = {
                    "text": row["Nội Dung"],
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
                }
                response = requests.post(URL, headers=HEADERS, json=payload)
                if response.status_code == 200:
                    mp3_path = row["Path"].replace(".txt", ".mp3")
                    with open(mp3_path, "wb") as f:
                        f.write(response.content)
                    status, note = "Thành Công", ""
                else:
                    status, note = "Thất Bại", response.text
            except Exception as e:
                status, note = "Thất Bại", str(e)
            self.tree.set(self.tree.get_children()[i], "Trạng Thái", status)
            self.tree.set(self.tree.get_children()[i], "Ghi Chú", note)
            self.colorize_row(self.tree.get_children()[i], status)

if __name__ == "__main__":
    root = tk.Tk()
    app = StatusTableApp(root)
    root.mainloop()
