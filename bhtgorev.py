import json
import os
from datetime import datetime
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, \
    QMessageBox, QFrame, QDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import qdarkstyle
from PyQt5.QtWidgets import QHBoxLayout 
from PyQt5.QtWidgets import QInputDialog  
from PyQt5.QtWidgets import QTabWidget, QTextEdit
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QMainWindow



PRIMARY_COLOR = "#405DE6"  
SECONDARY_COLOR = "#5851DB" 
BACKGROUND_COLOR = "#000000"  
TEXT_COLOR = "#FFFFFF"  

class Task:
    def __init__(self, name, description, content="", status="Not Started", created_at=None, person_name=None):
        self.name = name
        self.description = description
        self.content = content
        self.status = status
        self.created_at = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.person_name = person_name

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "status": self.status,
            "created_at": self.created_at,
            "person_name": self.person_name
        }


class TaskTrackerApp(QWidget):
    class TeamMembersDialog(QDialog):
        def __init__(self, team_members):
            super().__init__()

            self.team_members = team_members

            self.setWindowTitle("Ekip Üyeleri")
            self.setGeometry(300, 300, 500, 300)
            self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")

            layout = QVBoxLayout(self)

            self.team_members_list = QListWidget(self)
            for member in self.team_members:
                self.team_members_list.addItem(member)

            layout.addWidget(self.team_members_list)

            button_layout = QHBoxLayout()

            add_button = QPushButton("Ekip Üyesi Ekle", self)
            add_button.setStyleSheet(TaskTrackerApp.team_members_buttons_style())
            add_button.clicked.connect(self.add_team_member)
            button_layout.addWidget(add_button)

            remove_button = QPushButton("Ekip Üyesi Çıkar", self)
            remove_button.setStyleSheet(TaskTrackerApp.team_members_buttons_style())
            remove_button.clicked.connect(self.remove_team_member)
            button_layout.addWidget(remove_button)

            layout.addLayout(button_layout)

            self.save_button = QPushButton("Kaydet", self)
            self.save_button.setStyleSheet(TaskTrackerApp.team_members_buttons_style())
            self.save_button.clicked.connect(self.save_team_members)
            layout.addWidget(self.save_button)

        def add_team_member(self):
            member_name, ok = QInputDialog.getText(self, "Ekip Üyesi Ekle", "Ekip Üyesi Adı:")
            if ok and member_name:
                self.team_members.append(member_name)
                self.team_members_list.addItem(member_name)

        def remove_team_member(self):
            selected_item = self.team_members_list.currentItem()
            if selected_item:
                member_name = selected_item.text()
                self.team_members.remove(member_name)
                self.team_members_list.takeItem(self.team_members_list.row(selected_item))

        def save_team_members(self):
            with open("team_members.txt", "w") as file:
                for member in self.team_members:
                    file.write(member + "\n")

    @staticmethod
    def other_buttons_style():
        base_color = "#008CBA"  # Ana penceredeki buton rengi

        return f"""
            QPushButton {{
                background-color: {base_color};
                border: none;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #006799;
            }}
        """

    @staticmethod
    def team_members_buttons_style():
        return """
            QPushButton {
                background-color: #008B8B;  /* Koyu Turkuaz rengi */
                border: none;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #006666;  /* Koyu Turkuaz rengi, hover durumunda daha koyu ton */
            }
        """

    def __init__(self):
        super().__init__()
        self.team_members = []
        self.load_team_members()

        self.file_path = "tasks.json"
        self.tasks = []
        self.load_tasks()

        self.setWindowTitle("Black Hat Team Görev Sistemi # Developed By 404Qea")
        self.setGeometry(100, 100, 500, 800)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")

        logo_label = QLabel(self)
        logo_label.setGeometry(10, 10, 100, 100)
        logo_pixmap = QPixmap("/Users/404qea/Downloads/bhtlogo.jpeg")
        logo_label.setPixmap(logo_pixmap.scaled(logo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        task_frame = QFrame(self)
        task_frame.setGeometry(120, 10, 370, 100)
        task_frame.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR}; border-radius: 10px;")

        task_layout = QVBoxLayout(task_frame)
        self.task_label = QLabel("Black Hat Team Görev Sistemi", task_frame)
        self.task_label.setAlignment(Qt.AlignCenter)
        task_layout.addWidget(self.task_label)

        self.task_listbox = QListWidget(self)
        self.task_listbox.setGeometry(10, 120, 480, 300)
        self.task_listbox.setStyleSheet(
            f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; selection-background-color: {SECONDARY_COLOR};")
        self.task_listbox.itemDoubleClicked.connect(self.edit_task)

        self.add_button = QPushButton("Görev Ekle", self)
        self.add_button.setGeometry(10, 430, 480, 30)
        self.add_button.setStyleSheet(TaskTrackerApp.other_buttons_style())
        self.add_button.clicked.connect(self.add_task_window)

        self.list_button = QPushButton("Görevleri Listele", self)
        self.list_button.setGeometry(10, 470, 480, 30)
        self.list_button.setStyleSheet(TaskTrackerApp.other_buttons_style())
        self.list_button.clicked.connect(self.list_tasks)

        self.delete_button = QPushButton("Görevleri Sil", self)
        self.delete_button.setGeometry(10, 510, 480, 30)
        self.delete_button.setStyleSheet(TaskTrackerApp.other_buttons_style())
        self.delete_button.clicked.connect(self.delete_tasks)

        self.show_file_path_button = QPushButton("Dosya Yolunu Göster", self)
        self.show_file_path_button.setGeometry(10, 550, 480, 30)
        self.show_file_path_button.setStyleSheet(TaskTrackerApp.other_buttons_style())
        self.show_file_path_button.clicked.connect(self.show_file_path)

        self.view_content_button = QPushButton("Görev İçeriğini Görüntüle", self)
        self.view_content_button.setGeometry(10, 590, 480, 30)
        self.view_content_button.setStyleSheet(TaskTrackerApp.other_buttons_style())
        self.view_content_button.clicked.connect(self.view_content)

        self.show_team_members_button = QPushButton("Ekip Üyelerini Göster", self)
        self.show_team_members_button.setGeometry(10, 630, 480, 30)
        self.show_team_members_button.setStyleSheet(TaskTrackerApp.other_buttons_style())
        self.show_team_members_button.clicked.connect(self.show_team_members_dialog)

        self.reports_button = QPushButton("Raporlar", self)
        self.reports_button.setGeometry(10, 630, 480, 30)
        self.reports_button.setStyleSheet(TaskTrackerApp.other_buttons_style())
        self.reports_button.clicked.connect(self.show_reports_window)

        
        self.reports_button.move((self.width() - self.reports_button.width()) // 2, self.show_team_members_button.y() + self.show_team_members_button.height() + 10)

    def show_reports_window(self):
        reports_window = QMainWindow(self)
        reports_window.setWindowTitle("Görev Raporları")
        reports_window.setGeometry(300, 200, 800, 600)  
        reports_window.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")

        central_widget = QWidget(reports_window)
        reports_window.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        reports_label = QLabel("Görev Raporları", central_widget)
        reports_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        reports_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(reports_label)

        tab_widget = QTabWidget(central_widget)
        completed_tab = QWidget()
        incomplete_tab = QWidget()

        tab_widget.addTab(completed_tab, "Teslim Edenlerr")
        tab_widget.addTab(incomplete_tab, "Teslim Etmeyenlerr")

        completed_text_edit = QTextEdit(completed_tab)
        completed_text_edit.setGeometry(10, 10, 760, 480) 
        completed_text_edit.setPlainText(self.generate_task_report(True))

        incomplete_text_edit = QTextEdit(incomplete_tab)
        incomplete_text_edit.setGeometry(10, 10, 760, 480)  
        incomplete_text_edit.setPlainText(self.generate_task_report(False))

        layout.addWidget(tab_widget)

       
        save_and_exit_button = QPushButton("Kaydet ve Çıkış", central_widget)
        save_and_exit_button.setGeometry(10, 520, 760, 30)
        save_and_exit_button.setStyleSheet(TaskTrackerApp.other_buttons_style())
        save_and_exit_button.clicked.connect(lambda: self.save_reports(completed_text_edit.toPlainText(), incomplete_text_edit.toPlainText(), reports_window))
    def load_reports(self):
        if os.path.exists("completed_report.txt") and os.path.exists("incomplete_report.txt"):
            with open("completed_report.txt", "r") as completed_file:
                completed_report = completed_file.read()

            with open("incomplete_report.txt", "r") as incomplete_file:
                incomplete_report = incomplete_file.read()

            return completed_report, incomplete_report
        else:
            return "", ""

    def show_reports_window(self):
        reports_window = QMainWindow(self)
        reports_window.setWindowTitle("Görev Raporları")
        reports_window.setGeometry(300, 200, 800, 600)
        reports_window.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")

        central_widget = QWidget(reports_window)
        reports_window.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        reports_label = QLabel("Görev Raporları", central_widget)
        reports_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        reports_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(reports_label)

        tab_widget = QTabWidget(central_widget)
        completed_tab = QWidget()
        incomplete_tab = QWidget()

        tab_widget.addTab(completed_tab, "Teslim Edenler")
        tab_widget.addTab(incomplete_tab, "Teslim Etmeyenler")

        completed_text_edit = QTextEdit(completed_tab)
        completed_text_edit.setGeometry(10, 10, 760, 480)
        completed_report, incomplete_report = self.load_reports()
        completed_text_edit.setPlainText(completed_report)

        incomplete_text_edit = QTextEdit(incomplete_tab)
        incomplete_text_edit.setGeometry(10, 10, 760, 480)
        incomplete_text_edit.setPlainText(incomplete_report)

        layout.addWidget(tab_widget)

        save_and_exit_button = QPushButton("Kaydet ve Çıkış", central_widget)
        save_and_exit_button.setGeometry(10, 520, 760, 30)
        save_and_exit_button.setStyleSheet(TaskTrackerApp.other_buttons_style())
        save_and_exit_button.clicked.connect(lambda: self.save_reports(completed_text_edit.toPlainText(), incomplete_text_edit.toPlainText(), reports_window))

        reports_window.show()

    def save_reports(self, completed_report, incomplete_report, window):
        with open("completed_report.txt", "w") as completed_file:
            completed_file.write(completed_report)

        with open("incomplete_report.txt", "w") as incomplete_file:
            incomplete_file.write(incomplete_report)

        QMessageBox.information(self, "Başarı", "Raporlar başarıyla kaydedildi!")
        window.close()

        self.task_frame = QLabel(self)
        self.task_frame.setGeometry(10, 670, 80, 150)
        self.task_frame.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; border: 2px solid black;")
   
    def generate_task_report(self, tamamlanan=True):
        filtered_tasks = [task for task in self.tasks if task.status == ("Tamamlandı" if tamamlanan else "Başlamadı")]
        report_text = "\n".join([f"{task.name} - {task.person_name}" for task in filtered_tasks])
        return report_text

    @staticmethod
    def other_buttons_style():
        return """
            QPushButton {
                background-color: #008CBA;
                border: none;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #006799;
            }
        """

    def add_task_window(self):
        add_window = QWidget(self)
        add_window.setWindowTitle("Görev Ekle")
        add_window.setGeometry(200, 200, 300, 200)
        add_window.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")

        # Çıkış butonu ekle
        exit_button = QPushButton("Çıkış", add_window)
        exit_button.setGeometry(10, 10, 50, 20)
        exit_button.clicked.connect(add_window.close)

        name_label = QLabel("Görev Adı:", add_window)
        name_label.setGeometry(10, 40, 100, 20)
        name_entry = QLineEdit(add_window)
        name_entry.setGeometry(120, 40, 150, 20)

        desc_label = QLabel("Görev Açıklaması:", add_window)
        desc_label.setGeometry(10, 70, 100, 20)
        desc_entry = QLineEdit(add_window)
        desc_entry.setGeometry(120, 70, 150, 20)

        content_label = QLabel("Görev İçeriği:", add_window)
        content_label.setGeometry(10, 100, 100, 20)
        content_entry = QLineEdit(add_window)
        content_entry.setGeometry(120, 100, 150, 20)

        add_button = QPushButton("Ekle", add_window)
        add_button.setGeometry(10, 130, 260, 30)
        add_button.clicked.connect(lambda: self.add_task(name_entry.text(), desc_entry.text(), content_entry.text(), "", add_window))

        add_window.show()

    def add_task(self, name, description, content, person_name, add_window):
        if name and description:
            new_task = Task(name, description, content, person_name=person_name)
            self.tasks.append(new_task)
            self.save_tasks()
            add_window.close()
            QMessageBox.information(self, "Başarı", "Görev başarıyla eklendi!")
            self.list_tasks()
        else:
            QMessageBox.warning(self, "Uyarı", "Görev adı ve açıklaması boş olamaz.")

    def list_tasks(self):
        self.task_listbox.clear()
        for i, task in enumerate(self.tasks, start=1):
            self.task_listbox.addItem(f"{i}. {task.name} - {task.status}")

        task_text = "\n".join([f"{i}. {task.name}" for i, task in enumerate(self.tasks, start=1)])
        self.task_label.setText(task_text)

    def delete_tasks(self):
        selected_index = self.task_listbox.currentRow()
        if selected_index != -1:
            self.tasks.pop(selected_index)
            self.save_tasks()
            QMessageBox.information(self, "Başarı", "Görev başarıyla silindi!")
            self.list_tasks()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek bir görev seçin.")

    def edit_task(self, item):
        index = self.task_listbox.row(item)
        task = self.tasks[index]

        edit_window = QWidget(self)
        edit_window.setWindowTitle("Görevi Düzenle")
        edit_window.setGeometry(200, 200, 300, 200)
        edit_window.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")

        name_label = QLabel("Görev Adı:", edit_window)
        name_label.setGeometry(10, 10, 100, 20)
        name_entry = QLineEdit(edit_window)
        name_entry.setGeometry(120, 10, 150, 20)
        name_entry.setText(task.name)

        desc_label = QLabel("Görev Açıklaması:", edit_window)
        desc_label.setGeometry(10, 40, 100, 20)
        desc_entry = QLineEdit(edit_window)
        desc_entry.setGeometry(120, 40, 150, 20)
        desc_entry.setText(task.description)

        content_label = QLabel("Görev İçeriği:", edit_window)
        content_label.setGeometry(10, 70, 100, 20)
        content_entry = QLineEdit(edit_window)
        content_entry.setGeometry(120, 70, 150, 20)
        content_entry.setText(task.content)

        save_button = QPushButton("Değişiklikleri Kaydet", edit_window)
        save_button.setGeometry(10, 100, 260, 30)
        save_button.clicked.connect(lambda: self.save_edited_task(index, name_entry.text(), desc_entry.text(), content_entry.text(), edit_window))

        edit_window.show()

    def save_edited_task(self, index, name, description, content, edit_window):
        if name and description:
            edited_task = Task(name, description, content)
            self.tasks[index] = edited_task
            self.save_tasks()
            edit_window.close()
            QMessageBox.information(self, "Başarı", "Görev başarıyla düzenlendi!")
            self.list_tasks()
        else:
            QMessageBox.warning(self, "Uyarı", "Görev adı ve açıklaması boş olamaz.")

    def save_tasks(self):
        with open(self.file_path, "w") as file:
            tasks_data = [task.to_dict() for task in self.tasks]
            json.dump(tasks_data, file, indent=2)

    def load_tasks(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                tasks_data = json.load(file)
                self.tasks = [Task(**data) for data in tasks_data]

    def show_file_path(self):
        QMessageBox.information(self, "Dosya Yolu", f"Görevler şurada kaydediliyor: {self.file_path}")

    def view_content(self):
        selected_index = self.task_listbox.currentRow()
        if selected_index != -1:
            task = self.tasks[selected_index]
            QMessageBox.information(self, "Görev İçeriği", f"'{task.name}' için içerik:\n\n{task.content}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen içeriğini görmek istediğiniz bir görev seçin.")

    def show_team_members_dialog(self):
        team_members_dialog = TaskTrackerApp.TeamMembersDialog(self.team_members)
        result = team_members_dialog.exec_()

        if result == QDialog.Accepted:
            self.team_members = team_members_dialog.team_members
            self.save_team_members()

    def save_team_members(self):
        with open("team_members.txt", "w") as file:
            for member in self.team_members:
                file.write(member + "\n")

    def load_team_members(self):
        if os.path.exists("team_members.txt"):
            with open("team_members.txt", "r") as file:
                self.team_members = [line.strip() for line in file]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    try:
        window = TaskTrackerApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Hata oluştu: {e}")
