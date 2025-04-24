
import os

def get_txt_files(folder):
    files_data = []
    for i, filename in enumerate(sorted(os.listdir(folder))):
        if filename.endswith(".txt"):
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
