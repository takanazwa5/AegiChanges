import resources_rc
import os
from difflib import Differ
from PySide6 import QtCore, QtWidgets, QtGui

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.oldFile = []
        self.newFile = []
        self.savePath = ""
        
        self.app = app
        self.setWindowTitle("AegiChanges")
        self.setWindowIcon(QtGui.QIcon(":/icon.png"))
        
        self.oldFileButton = QtWidgets.QPushButton("Load old file...")
        self.oldFileButton.pressed.connect(self.loadOldFile)
        
        self.newFileButton = QtWidgets.QPushButton("Load new file...")
        self.newFileButton.pressed.connect(self.loadNewFile)

        self.saveFileCheckbox = QtWidgets.QCheckBox("Save changes to file")
        
        self.compareButton = QtWidgets.QPushButton("Compare")
        self.compareButton.pressed.connect(self.compareFiles)

        buttonsHolder = QtWidgets.QWidget()
        buttonsHolder.setLayout(QtWidgets.QHBoxLayout())
        buttonsHolder.layout().addWidget(self.oldFileButton)
        buttonsHolder.layout().addWidget(self.newFileButton)
        buttonsHolder.layout().addWidget(self.compareButton)
        buttonsHolder.layout().addWidget(self.saveFileCheckbox)
        
        self.output = TextEdit()

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(QtWidgets.QVBoxLayout())
        centralWidget.layout().addWidget(buttonsHolder)
        centralWidget.layout().addWidget(self.output)
        
        self.setCentralWidget(centralWidget)
        self.showMaximized()

    def setUIDisabled(self, value):
        self.oldFileButton.setDisabled(value)
        self.newFileButton.setDisabled(value)
        self.compareButton.setDisabled(value)
        self.saveFileCheckbox.setDisabled(value)
        
    def loadOldFile(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Load old file", filter="ASS files (*.ass)")[0]
        if filePath:
            try:
                with open(filePath, "r", encoding="utf-8") as f:
                    self.oldFile = f.readlines()
                    self.oldFileButton.setStyleSheet("background-color: darkgreen")
            except Exception as e:
                self.output.appendError(f"Error loading old file: {e}")
                self.oldFileButton.setStyleSheet("background-color: darkred")

    def loadNewFile(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Load new file", filter="ASS files (*.ass)")[0]
        if filePath:
            self.savePath = os.path.dirname(filePath)
            print(self.savePath)
            try:
                with open(filePath, "r", encoding="utf-8") as f:
                    self.newFile = f.readlines()
                    self.newFileButton.setStyleSheet("background-color: darkgreen")
            except Exception as e:
                self.output.appendError(f"Error loading new file: {e}")
                self.newFileButton.setStyleSheet("background-color: darkred")

    def extractEventsSection(self, file):
        eventsSectionIndex = file.index("[Events]\n")
        return file[eventsSectionIndex + 2:]
    
    def cleanEvents(self, events):
        for line in events:
            format = line.split(":", 1)[0]
            start = line.split(",", 2)[1]
            end = line.split(",", 3)[2]
            text = line.split(",", 9)[-1]
            format += " " if format == "Comment" else ""
            line = f"{format} | {start} | {end} | {text}"
            yield line

    def compareFiles(self):
        self.output.clear()

        if not self.oldFile:
            self.output.appendError("Old file not loaded")
            return
        
        if not self.newFile:
            self.output.appendError("New file not loaded")
            
        oldEvents = self.extractEventsSection(self.oldFile)
        newEvents = self.extractEventsSection(self.newFile)
        
        if not oldEvents:
            self.output.appendError("[Events] section not found in old file")
            return
        
        if not newEvents:
            self.output.appendError("[Events] section not found in new file")
            return
        
        self.setUIDisabled(True)
        
        oldEvents = list(self.cleanEvents(oldEvents))
        newEvents = list(self.cleanEvents(newEvents))
        
        differ = Differ()
        diff = list(differ.compare(oldEvents, newEvents))

        for i in range(len(diff)):
            previousLine = diff[i - 1] if i > 0 else ""
            line = diff[i]
            nextLine = diff[i + 1] if i + 1 < len(diff) else ""

            if line.startswith("-"):
                if nextLine.startswith("?"):
                    for j in range(len(line)):
                        if j < len(nextLine):
                            if not nextLine[j] in [" ", "?"]:
                                self.output.appendRemovedHighlighted(line[j])
                                continue
                        self.output.appendRemoved(line[j])
                elif nextLine.startswith("+"):
                    self.output.appendRemoved(line)
                else:
                    self.output.appendRemovedHighlighted(line)

            elif line.startswith("+"):
                if nextLine.startswith("?"):
                    for j in range(len(line)):
                        if j < len(nextLine):
                            if not nextLine[j] in [" ", "?"]:
                                self.output.appendAddedHighlighted(line[j])
                                continue
                        self.output.appendAdded(line[j])
                elif previousLine.startswith("?"):
                    self.output.appendAdded(line)
                else:
                    self.output.appendAddedHighlighted(line)

            elif not line.startswith("?"):
                self.output.appendUnchangedLine(line)

        if self.saveFileCheckbox.isChecked():
            try:
                with open(os.path.join(self.savePath, "changes.diff"), "w", encoding="utf-8") as f:
                    f.write(self.output.toPlainText())
            except Exception as e:
                self.output.appendError(f"Error saving file: {e}")

        self.setUIDisabled(False)

class TextEdit(QtWidgets.QTextEdit):
    def __init__(self):
        super().__init__()
        self.defaultBgColor = QtGui.QColor.fromRgbF(0, 0, 0, 0)
        self.setReadOnly(True)
        self.setFontPointSize(10)
        self.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        preferredFonts = ["JetBrains Mono", "Consolas"]
        for font in preferredFonts:
            if font in QtGui.QFontDatabase.families():
                self.setFont(QtGui.QFont(font))
                break

    def appendError(self, text):
        self.setTextBackgroundColor(self.defaultBgColor)
        self.setFontWeight(QtGui.QFont.Weight.Bold)
        self.setTextColor(QtGui.QColor("red"))
        self.append(text)
        self.setTextColor(QtGui.QColor("white"))
        self.setFontWeight(QtGui.QFont.Weight.Normal)

    def appendRemoved(self, text):
        if not self.textBackgroundColor() == QtGui.QColor("darkRed"):
            self.setTextBackgroundColor(QtGui.QColor("darkRed"))
        self.insertPlainText(text)
        QtWidgets.QApplication.processEvents()

    def appendRemovedHighlighted(self, text):
        if not self.textBackgroundColor() == QtGui.QColor("red"):
            self.setTextBackgroundColor(QtGui.QColor("red"))
        self.insertPlainText(text)
        QtWidgets.QApplication.processEvents()

    def appendAdded(self, text):
        if not self.textBackgroundColor() == QtGui.QColor("darkGreen"):
            self.setTextBackgroundColor(QtGui.QColor("darkGreen"))
        self.insertPlainText(text)
        QtWidgets.QApplication.processEvents()

    def appendAddedHighlighted(self, text):
        if not self.textBackgroundColor() == QtGui.QColor("green"):
            self.setTextBackgroundColor(QtGui.QColor("green"))
        self.insertPlainText(text)
        QtWidgets.QApplication.processEvents()

    def appendUnchangedLine(self, text):
        if not self.textBackgroundColor() == self.defaultBgColor:
            self.setTextBackgroundColor(self.defaultBgColor)
        self.insertPlainText(text)
        QtWidgets.QApplication.processEvents()    

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow(app)
    app.exec()