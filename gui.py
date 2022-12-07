import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from screeninfo import get_monitors



def submit(actionBox, pathButton, projectBox, vmhostBox, startBox, configureBox):
    args = "-" + actionBox.currentText().lower()
    args += " \"" + pathButton.text() + "\""
    args += " -project " + projectBox.toPlainText()
    args += " -vmhost " + vmhostBox.toPlainText()
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
    stylesheet = "./stylesheet.css"
    with open(stylesheet, "r") as fh:
        app.setStyleSheet(fh.read())
    window = QWidget()
    window.setMinimumSize(int(0.4*screens[0].width), int(0.65*screens[0].height))
    window.resize(int(0.55*screens[0].width), int(0.67*screens[0].height))
    window.setWindowTitle("GNScript")

    p = QPalette()
    gradient = QLinearGradient(0, 0, 0, 720)
    gradient.setColorAt(0.0, QColor(118, 60, 188))
    gradient.setColorAt(1.0, QColor(0, 164, 205))
    p.setBrush(QPalette.Window, QBrush(gradient))
    window.setPalette(p)

    vBoxCanvas = QVBoxLayout(objectName="vBoxCanvas")
    vBoxCanvas.setAlignment(Qt.AlignCenter)
    # vBoxCanvas.setContentsMargins(0,0,0,0)

    whiteCanvas = QWidget(objectName="whiteCanvas")
    whiteCanvas.setFixedSize(int(0.33*screens[0].width), int(0.55*screens[0].height))
    whiteCanvasShadow = QGraphicsDropShadowEffect(objectName="whiteCanvasShadow")
    whiteCanvasShadow.setXOffset(0)
    whiteCanvasShadow.setYOffset(0)
    whiteCanvasShadow.setBlurRadius(100)
    whiteCanvas.setGraphicsEffect(whiteCanvasShadow)

    logo = QSvgWidget("logo prototype.svg")
    logo.setFixedHeight(130)
    logo.setFixedWidth(250)
    welcomeLabel = QLabel("GNScript", objectName="welcomeLabel")
    actionLabel = QLabel("ACTION", objectName="actionLabel")
    pathLabel = QLabel("PATH", objectName="pathLabel")
    projectLabel = QLabel("PROJECT", objectName="projectLabel")
    vmhostLabel = QLabel("VMHOST", objectName="vmhostLabel")

    actionBox = QComboBox(objectName="actionBox")
    actionBox.addItems(["Load","Save"])
    pathButton = QPushButton("...",objectName="pathButton")
    projectBox = QTextEdit(objectName="projectBox")
    projectBox.setFixedHeight(25)
    vmhostBox = QTextEdit(objectName="vmhostBox")
    vmhostBox.setFixedHeight(25)

    startBox = QCheckBox("Start Nodes", objectName="startBox")
    configureBox = QCheckBox("Configure Nodes", objectName="configureBox")
    configureBox.setDisabled(True)

    verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

    submitButton = QPushButton("Submit",objectName="submitButton")

    vBoxContent = QVBoxLayout()
    vBoxContent.addWidget(logo)
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
    vBoxContent.addItem(verticalSpacer)
    vBoxContent.addWidget(submitButton)
    vBoxContent.setContentsMargins(30,50,30,30)
    vBoxContent.setSpacing(10)

    vBoxCanvas.addWidget(whiteCanvas)
    whiteCanvas.setFont(QFont("Arial"))
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

