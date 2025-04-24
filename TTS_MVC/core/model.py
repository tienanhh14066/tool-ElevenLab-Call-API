import os
import time

def get_txt_files(folder):
    txt_files = sorted(f for f in os.listdir(folder) if f.endswith(".txt"))
    files_data = []
    for i, filename in enumerate(txt_files):
        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        files_data.append({
            "STT": i + 1,
            "Tên txt": filename,
            "Nội Dung": content,
            "Trạng Thái": "Chờ",
            "Ghi Chú": "",
            "Path": path
        })
    return files_data

def update_txt_file(filepath, new_content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content.strip())

def run_all_tts(data, callback_per_row, delay_sec=0.5):
    for i, row in enumerate(data):
        if row["Trạng Thái"] in ["Chờ", "Thất Bại"]:
            callback_per_row(i)
            time.sleep(delay_sec)
