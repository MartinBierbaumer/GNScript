import sys
import os
import ipaddress
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


def checkSubmit(actionBox, pathButton, projectBox, vmhostBox, startBox, configureBox):
    if pathButton.text() == "...":
        errorMessage("Path field empty: Please select a Path")
        return

    if projectBox.toPlainText() == "":
        errorMessage("Project field empty: Please enter a choose a project")
        return

    try:
        address = ipaddress.ip_address(vmhostBox.toPlainText())
    except:
        errorMessage("Please enter a valid IPv4/IPv6 Address")
        return

    submit(actionBox, pathButton, projectBox, vmhostBox, startBox, configureBox)


def errorMessage(text):
    msg = QMessageBox()
    msg.setWindowTitle("GNScript")
    msg.setText(text)
    msg.exec_()


def setStylesheet(app, path):
    with open(path, "r") as fh:
        app.setStyleSheet(fh.read())


def openPath(actionBox, pathButton):
    if actionBox.currentText() == "Load":
        openFile = QFileDialog()
        openFile.exec_()
        try:
            file = openFile.selectedFiles()
            pathButton.setText(*file)
        except:
            print("Error: No File opened")
    else:
        folder = str(QFileDialog.getExistingDirectory(pathButton, "Select Directory"))
        try:
            pathButton.setText(folder)
        except:
            print("Error: No Folder opened")


def clickStart(startBox, configureBox):
    if startBox.isChecked():
        configureBox.setDisabled(False)
    else:
        configureBox.setChecked(False)
        configureBox.setDisabled(True)


def checkAction(startBox, configureBox, actionBox, pathButton):
    pathButton.setText("...")
    if actionBox.currentText() == "Save":
        startBox.setDisabled(True)
        startBox.setChecked(False)
        configureBox.setDisabled(True)
        configureBox.setChecked(False)
    else:
        startBox.setDisabled(False)


def main():
    app = QApplication([])
    setStylesheet(app, "./stylesheet.css")

    screens = []
    for m in get_monitors():
        screens.append(m)
        print(m)

    window = QWidget()
    window.setMinimumSize(int(0.4 * screens[0].width), int(0.65 * screens[0].height))
    window.resize(int(0.55 * screens[0].width), int(0.67 * screens[0].height))
    window.setWindowTitle("GNScript")

    p = QPalette()
    gradient = QLinearGradient(0, 0, 0, 720)
    gradient.setColorAt(0.0, QColor(118, 60, 188))
    gradient.setColorAt(1.0, QColor(0, 164, 205))
    p.setBrush(QPalette.Window, QBrush(gradient))
    window.setPalette(p)

    vBoxCanvas = QVBoxLayout(objectName="vBoxCanvas")
    vBoxCanvas.setAlignment(Qt.AlignCenter)

    whiteCanvas = QWidget(objectName="whiteCanvas")
    whiteCanvas.setFixedSize(int(0.33 * screens[0].width), int(0.55 * screens[0].height))
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

    widgetHeight = int(0.02315*screens[0].height)
    widgetHeight2 = int(0.025*screens[0].height)
    submitButtonHeight = int(0.0324*screens[0].height)
    print(widgetHeight)
    actionBox = QComboBox(objectName="actionBox")
    actionBox.addItems(["Load", "Save"])
    actionBox.setFixedHeight(widgetHeight2)
    pathButton = QPushButton("...", objectName="pathButton")
    pathButton.setFixedHeight(widgetHeight)
    projectBox = QTextEdit(objectName="projectBox")
    projectBox.setFixedHeight(widgetHeight)
    vmhostBox = QTextEdit(objectName="vmhostBox")
    vmhostBox.setFixedHeight(widgetHeight)

    startBox = QCheckBox("Start Nodes", objectName="startBox")
    configureBox = QCheckBox("Configure Nodes", objectName="configureBox")
    configureBox.setDisabled(True)

    verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

    submitButton = QPushButton("Submit", objectName="submitButton")
    submitButton.setFixedHeight(submitButtonHeight)

    vBoxContent = QVBoxLayout()
    for widget in [welcomeLabel, actionLabel, actionBox, pathLabel, pathButton, projectLabel, projectBox, vmhostLabel, vmhostBox, startBox,
                   configureBox, verticalSpacer, submitButton]:
        if widget == verticalSpacer:
            vBoxContent.addItem(widget)
            continue
        vBoxContent.addWidget(widget)

    vBoxContent.setContentsMargins(30, 50, 30, 30)
    vBoxContent.setSpacing(10)

    vBoxCanvas.addWidget(whiteCanvas)
    whiteCanvas.setLayout(vBoxContent)

    pathButton.clicked.connect(lambda: openPath(actionBox, pathButton))
    submitButton.clicked.connect(
        lambda: checkSubmit(actionBox, pathButton, projectBox, vmhostBox, startBox, configureBox))
    actionBox.currentTextChanged.connect(lambda: checkAction(startBox, configureBox, actionBox, pathButton))
    startBox.stateChanged.connect(lambda: clickStart(startBox, configureBox))

    window.setLayout(vBoxCanvas)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
