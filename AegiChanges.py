import os
from difflib import Differ
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QGridLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QMenuBar,
)


# GRAY: #24292E
# RED: #B31D28
# GREEN: #22863A
# DARKRED: #450C0F
# DARKGREEN: #113A1B


old_file : list[str] = []
new_file : list[str] = []


def on_load_file_button_pressed(file: list[str], label: QLabel) -> None:
    load_file(file, label)


def on_compare_button_pressed() -> None:
    window.output.clear()

    if len(old_file) == 0 and len(new_file) == 0:
        print_line("Files not selected")
        return

    if len(old_file) == 0:
        print_line("Old file not selected")
        return

    if len(new_file) == 0:
        print_line("New file not selected")
        return
    
    compare_result : list[str] = compare_files(old_file, new_file)
    print_changes(compare_result)


def load_file(file_var: list[str], label: QLabel) -> None:
    file_path = QFileDialog.getOpenFileName(filter="ASS files (*.ass)")[0]

    if file_path:
        label.setText(os.path.basename(file_path))

        with open(file_path, "r", encoding="utf-8") as f:
            file_var[:] = f.readlines()


def extract_events(file: list[str]) -> list[str]:
    try:
        events_index : int = file.index("[Events]\n")
    except ValueError:
        return []

    return file[events_index + 2:]


def clean_events(file: list[str]) -> list[str]:
    result : list[str] = []

    for line in file:
        parts = line.split(",", maxsplit=9)

        parts[0] = parts[0].split(":", maxsplit=1)[0] + ": "
        if parts[0] == "Comment: ":
            parts[0] += "\u00A0"

        if parts[3] == "TLmode" or line == "":
            continue
        
        result.append(f"{parts[0]}{parts[1]}, {parts[2]}, {parts[-1]}")


    return result


def compare_files(old_file: list[str], new_file: list[str]) -> list[str]:
    old_file = extract_events(old_file)
    new_file = extract_events(new_file)

    if len(old_file) == 0 and len(new_file) == 0:
        print_line("[Events] section not found in both files")
        return []
    
    if len(old_file) == 0:
        print_line("[Events] section not found in old file")
        return []

    if len(new_file) == 0:
        print_line("[Events] section not found in new file")
        return []

    old_file = clean_events(old_file)
    new_file = clean_events(new_file)

    return list(Differ().compare(old_file, new_file))


def print_line(text: str) -> None:
    window.output.append(text.replace("\n", ""))


def print_changes(compare_result: list[str]) -> None:
    for line in compare_result:

        if line.startswith("-"):
            print_line(f"<span style='background-color: #450C0F; color: white; font-family: Consolas'>{line}</span>")
        
        elif line.startswith("+"):
            print_line(f"<span style='background-color: #113A1B; color: white; font-family: Consolas'>{line}</span>")
        
        elif not line.startswith("?"):
            print_line(line)


def save_changes_to_file(type: str) -> None:
    match type:
        case "txt":
            filter = "Text files (*.txt)"
        case "html":
            filter = "HTML files (*.html)"
        case "diff":
            filter = "Diff files (*.diff)"

    file_to_save = QFileDialog.getSaveFileName(filter=filter)[0]

    if file_to_save:
        try:
            with open(file_to_save, "w", encoding="utf-8") as f:
                if type in ["txt", "diff"]:
                    f.write(window.output.toPlainText())
                elif type == "html":
                    html_file = window.output.toHtml()
                    html_file = html_file.replace('<body style="', \
                    '<body style="background-color: #24292E; color: white;', 1)
                    f.write(html_file)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred while saving changes to file: {str(e)}")


app = QApplication([])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AegiChanges")

        menubar = QMenuBar()
        self.setMenuBar(menubar)

        file_menu = menubar.addMenu("File")
        file_menu.addAction("Save changes to text file", lambda: save_changes_to_file("txt"))
        file_menu.addAction("Save changes to html file", lambda: save_changes_to_file("html"))
        file_menu.addAction("Save changes to diff file", lambda: save_changes_to_file("diff"))
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        layout = QGridLayout()

        old_file_button = QPushButton("Load old file")
        old_file_button.clicked.connect(lambda: on_load_file_button_pressed(old_file, old_file_label))

        new_file_button = QPushButton("Load new file")
        new_file_button.clicked.connect(lambda: on_load_file_button_pressed(new_file, new_file_label))
        
        old_file_label = QLabel()
        old_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        new_file_label = QLabel()
        new_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        compare_button = QPushButton("Compare Files")
        compare_button.clicked.connect(on_compare_button_pressed)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFontFamily("Consolas")

        layout.addWidget(old_file_button, 0, 0)
        layout.addWidget(old_file_label, 1, 0)
        layout.addWidget(new_file_button, 0, 1)
        layout.addWidget(new_file_label, 1, 1)
        layout.addWidget(compare_button, 0, 2)
        layout.addWidget(self.output, 2, 0, 1, 3)

        widget = QWidget()
        widget.setLayout(layout)
        self.setStyleSheet(".QTextEdit, .QWidget {background-color: #24292E; color: white;} .QLabel {color: white;}")
        self.setCentralWidget(widget)
    
window = MainWindow()
window.showMaximized()
app.exec()