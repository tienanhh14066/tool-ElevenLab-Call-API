import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QHBoxLayout, QToolButton, QDialog, QLabel, QTextEdit, QDialogButtonBox, QApplication
)
from PyQt5.QtCore import Qt
from controller.app_controller import AppController
from core.status import STATUS_WAIT, STATUS_SUCCESS, STATUS_FAILED

class EditDialog(QDialog):
    def __init__(self, filename, content, on_save):
        super().__init__()
        self.setWindowTitle(f"Sửa nội dung - {filename}")
        self.resize(400, 300)
        self.textbox = QTextEdit()
        self.textbox.setText(content)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>{filename}</b>"))
        layout.addWidget(self.textbox)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.on_save = on_save

    def accept(self):
        self.on_save(self.textbox.toPlainText().strip())
        super().accept()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TTS App - Phase 1.5 (MVC)")
        self.resize(1050, 650)
        self.controller = AppController()

        layout = QVBoxLayout()
        self.select_btn = QPushButton("📂 Chọn thư mục")
        self.select_btn.clicked.connect(self.select_folder)
        self.start_all_btn = QPushButton("▶️ Bắt đầu")
        self.start_all_btn.clicked.connect(self.handle_run_all_tts)
        layout.addWidget(self.select_btn)
        layout.addWidget(self.start_all_btn)

        self.info_label = QLabel("📂 Chưa chọn thư mục")
        layout.addWidget(self.info_label)

        self.table = QTableWidget(0, 7)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["STT", "Tên txt", "Nội Dung", "Trạng Thái", "Progress", "Ghi Chú", "Hành Động"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục")
        if folder:
            stats = self.controller.load_folder(folder)
            self.info_label.setText(
                f"📂 {stats['path']} | 📄 Tổng: {stats['total']} | ✅ Đã gen: {stats['done']} | ❌ Chưa/Lỗi: {stats['pending']}"
            )
            self.populate_table(self.controller.loaded_data)

    def populate_table(self, data):
        self.table.setRowCount(0)
        for i, row in enumerate(data):
            self.table.insertRow(i)
            for j, key in enumerate(["STT", "Tên txt", "Nội Dung", "Trạng Thái"]):
                item = QTableWidgetItem(str(row[key]))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(i, j, item)

            progress_item = QTableWidgetItem(row.get("Progress", ""))
            progress_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(i, 4, progress_item)

            ghi_chu_item = QTableWidgetItem(str(row.get("Ghi Chú", "")))
            ghi_chu_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(i, 5, ghi_chu_item)

            action_widget = QWidget()
            hbox = QHBoxLayout()
            hbox.setContentsMargins(0, 0, 0, 0)

            edit_btn = QToolButton()
            edit_btn.setText("🛠")
            edit_btn.clicked.connect(lambda _, r=i: self.open_edit_dialog(r))
            hbox.addWidget(edit_btn)

            tts_btn = QPushButton("🔊 Gọi TTS")
            if row["Trạng Thái"] == STATUS_FAILED:
                tts_btn.clicked.connect(lambda _, r=i: self.call_api(r))
                hbox.addWidget(tts_btn)

            action_widget.setLayout(hbox)
            self.table.setCellWidget(i, 6, action_widget)

    def open_edit_dialog(self, row):
        file_name = self.table.item(row, 1).text()
        old_content = self.table.item(row, 2).text()

        def on_save(new_text):
            self.controller.save_edited(row, new_text)
            self.table.item(row, 2).setText(new_text)

        dlg = EditDialog(file_name, old_content, on_save)
        dlg.exec_()

    def call_api(self, row):
        self.table.item(row, 3).setText("Đang xử lý")
        self.table.item(row, 4).setText("...")
        self.table.item(row, 5).setText("")

        def callback(index, updated_row):
            self.table.item(index, 3).setText(updated_row["Trạng Thái"])
            self.table.item(index, 4).setText(updated_row.get("Progress", ""))
            self.table.item(index, 5).setText(updated_row["Ghi Chú"])

        self.controller.call_api(row, callback)
    
    def handle_run_all_tts(self):
        self.controller.run_all_tts(lambda idx: (
        self.call_api(idx),
        QApplication.processEvents()
    ))

