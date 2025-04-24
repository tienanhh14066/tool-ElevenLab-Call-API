import os
from core.model import get_txt_files, update_txt_file
from core.api import call_tts_api, TTSResponse
from core.status import STATUS_SUCCESS, STATUS_WAIT, STATUS_FAILED

class AppController:
    def __init__(self):
        self.loaded_data = []
        self.folder_path = ""

    def load_folder(self, folder):
        self.folder_path = folder
        self.loaded_data = get_txt_files(folder)

        for row in self.loaded_data:
            mp3_path = row["Path"].replace(".txt", ".mp3")
            if os.path.exists(mp3_path):
                row["Trạng Thái"] = STATUS_SUCCESS
                row["Ghi Chú"] = ""
            else:
                row["Trạng Thái"] = STATUS_WAIT
                row["Ghi Chú"] = ""

        total = len(self.loaded_data)
        done = sum(1 for r in self.loaded_data if r["Trạng Thái"] == STATUS_SUCCESS)
        pending = total - done
        return {
            "path": folder,
            "total": total,
            "done": done,
            "pending": pending
        }

    def save_edited(self, index, new_content):
        self.loaded_data[index]["Nội Dung"] = new_content
        update_txt_file(self.loaded_data[index]["Path"], new_content)

    def call_api(self, index, callback):
        row = self.loaded_data[index]
        def wrapped(result: TTSResponse):
            if result.success and result.content:
                mp3_path = row["Path"].replace(".txt", ".mp3")
                with open(mp3_path, "wb") as f:
                    f.write(result.content)
                row["Trạng Thái"] = STATUS_SUCCESS
                row["Ghi Chú"] = ""
            else:
                row["Trạng Thái"] = STATUS_FAILED
                row["Ghi Chú"] = result.error or "Lỗi không xác định"
            callback(index, row)
        call_tts_api(row["Nội Dung"], wrapped)