import sys
import os
import threading
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


def submit(actionBox, pathButton, projectBox, vmhostBox, startBox, configureBox):
    args = "-"+actionBox.currentText().lower()
    args += " \""+pathButton.text()+"\""
    args += " -project "+projectBox.toPlainText()
    args += " -vmhost "+vmhostBox.toPlainText()
    if startBox.isChecked():
        args += " -start"

    if configureBox.isChecked():
        args += " -configure "
    print(args)
    os.system("python3 ./skript.py " + args)


def openPath(actionBox,pathButton):
    if (actionBox.currentText() == "Load"):
        openFile = QFileDialog()
        openFile.exec_()
        try:
            file = openFile.selectedFiles()
            pathButton.setText(*file)
        except:
            print("Error: No File opened")
    elif (actionBox.currentText() == "Save"):
        folder = str(QFileDialog.getExistingDirectory(pathButton, "Select Directory"))
        try:
            pathButton.setText(folder)
        except:
            print("Error: No Folder opened")

def clickStart(startBox,configureBox):
    if startBox.isChecked():
        configureBox.setDisabled(False)
    else:
        configureBox.setChecked(False)
        configureBox.setDisabled(True)

def resetPath(pathButton):
    pathButton.setText("...")

def main():
    app = QApplication([])
    window = QWidget()
    window.setMinimumSize(1000, 720)
    window.setWindowTitle("GNScript")
    p = QPalette()
    gradient = QLinearGradient(0, 0, 0, 720)
    gradient.setColorAt(0.0, QColor(118, 60, 188))
    gradient.setColorAt(1.0, QColor(0, 164, 205))
    p.setBrush(QPalette.Window, QBrush(gradient))
    window.setPalette(p)

    vBoxCanvas = QVBoxLayout()
    vBoxCanvas.setAlignment(Qt.AlignCenter)
    # vBoxCanvas.setContentsMargins(0,0,0,0)

    whiteCanvas = QWidget()
    whiteCanvas.setFixedSize(630,590)
    whiteCanvas.setStyleSheet("background-color: white; border-radius: 30px")
    whiteCanvasShadow = QGraphicsDropShadowEffect()
    whiteCanvasShadow.setXOffset(0)
    whiteCanvasShadow.setYOffset(0)
    whiteCanvasShadow.setBlurRadius(100)
    whiteCanvas.setGraphicsEffect(whiteCanvasShadow)

    welcomeLabel = QLabel("GNScript")
    actionLabel = QLabel("ACTION")
    pathLabel = QLabel("PATH")
    projectLabel = QLabel("PROJECT")
    vmhostLabel = QLabel("VMHOST")

    welcomeLabel.setStyleSheet("font-size: 45px; font-weight: bold")
    actionBox = QComboBox()
    actionBox.addItems(["Load","Save"])
    actionBox.setStyleSheet("* { border-radius: 0 } QComboBox { background-color: #e6e6e6; border-radius: 5px; height: 27px } QComboBox::drop-down { border: 0px } QComboBox::down-arrow { image: url(C:/Users/maxin/PycharmProjects/pythonProject/arrow.ico); width: 12px; margin-right: 5px; border: 0px }")
    pathButton = QPushButton("...")
    pathButton.setStyleSheet("background-color: #e6e6e6; border-radius: 5px; height: 25px")
    projectBox = QTextEdit()
    projectBox.setStyleSheet("background-color: #e6e6e6; border-radius: 5px")
    projectBox.setFixedHeight(25)
    vmhostBox = QTextEdit()
    vmhostBox.setStyleSheet("background-color: #e6e6e6; border-radius: 5px")
    vmhostBox.setFixedHeight(25)

    startBox = QCheckBox("Start Nodes")
    configureBox = QCheckBox("Configure Nodes")
    configureBox.setDisabled(True)

    submitButton = QPushButton("Submit")
    submitButton.setStyleSheet("text-align: center; background-color: #464646; color: white; height: 35px; border-radius:7px;")

    vBoxContent = QVBoxLayout()
    vBoxContent.addWidget(welcomeLabel)
    vBoxContent.addWidget(actionLabel)
    vBoxContent.addWidget(actionBox)
    vBoxContent.addWidget(pathLabel)
    vBoxContent.addWidget(pathButton)
    vBoxContent.addWidget(projectLabel)
    vBoxContent.addWidget(projectBox)
    vBoxContent.addWidget(vmhostLabel)
    vBoxContent.addWidget(vmhostBox)
    vBoxContent.addWidget(startBox)
    vBoxContent.addWidget(configureBox)
    vBoxContent.addWidget(submitButton)
    vBoxContent.setContentsMargins(20,50,20,100)

    vBoxCanvas.addWidget(whiteCanvas)

    whiteCanvas.setLayout(vBoxContent)

    pathButton.clicked.connect(lambda: openPath(actionBox,pathButton))
    submitButton.clicked.connect(lambda: submit(actionBox,pathButton,projectBox,vmhostBox,startBox,configureBox))
    startBox.stateChanged.connect(lambda: clickStart(startBox,configureBox))
    actionBox.currentTextChanged.connect(lambda: resetPath(pathButton))

    window.setLayout(vBoxCanvas)
    window.show()
    app.exec()

if __name__ == '__main__':
    main()

