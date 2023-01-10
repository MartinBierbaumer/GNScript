import threading
import os
import ipaddress
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from screeninfo import get_monitors

def execute(command):
    os.system(command)

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
    thread = threading.Thread(target=execute, args=("python3 ./skript.py " + args, ))
    thread.start()


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
    folder = str(QFileDialog.getExistingDirectory(pathButton, "Select Directory"))
    if folder == "":
        pathButton.setText("...")
    else:
        pathButton.setText(folder)

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
        startBox.setChecked(True)
        configureBox.setChecked(True)

def getDisplayResolution():
    screens = []
    for m in get_monitors():
        screens.append(m)
    return screens

def main():
    app = QApplication([])
    setStylesheet(app, "./stylesheet.css")

    screens = getDisplayResolution()
    screenWidth = screens[0].width
    screenHeight = screens[0].height

    window = QWidget()
    window.setMinimumSize(int(0.4 * screenWidth), int(0.65 * screenHeight))
    window.resize(int(0.55 * screenWidth), int(0.67 * screenHeight))
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
    whiteCanvas.setFixedSize(int(0.33 * screenWidth), int(0.55 * screenHeight))
    whiteCanvasShadow = QGraphicsDropShadowEffect(objectName="whiteCanvasShadow")
    whiteCanvasShadow.setXOffset(0)
    whiteCanvasShadow.setYOffset(0)
    whiteCanvasShadow.setBlurRadius(100)
    whiteCanvas.setGraphicsEffect(whiteCanvasShadow)

    logo = QSvgWidget("logo prototype.svg", objectName="logo")
    logo.setFixedHeight(int(0.131*screenHeight))
    logo.setFixedWidth(int(0.231*screenHeight))
    welcomeLabel = QLabel("GNScript", objectName="welcomeLabel")
    actionLabel = QLabel("ACTION", objectName="actionLabel")
    pathLabel = QLabel("PATH", objectName="pathLabel")
    projectLabel = QLabel("PROJECT NAME", objectName="projectLabel")
    vmhostLabel = QLabel("VMHOST", objectName="vmhostLabel")

    widgetHeight = int(0.02315*screenHeight)
    widgetHeight2 = int(0.025*screenHeight)
    submitButtonHeight = int(0.0324*screenHeight)

    actionBox = QComboBox(objectName="actionBox")
    actionBox.addItems(["Load", "Save"])
    actionBox.setFixedHeight(widgetHeight2)
    actionBox.setStyleSheet("QComboBox::down-arrow { image: url(./arrow.ico); width: "+str(int(0.007*screenWidth))+"px; margin-right: "+str(int(0.003*screenWidth))+"px; border: 0px }")
    pathButton = QPushButton("...", objectName="pathButton")
    pathButton.setFixedHeight(widgetHeight)
    projectBox = QTextEdit(objectName="projectBox")
    projectBox.setFixedHeight(widgetHeight)
    vmhostBox = QTextEdit(objectName="vmhostBox")
    vmhostBox.setFixedHeight(widgetHeight)

    startBox = QCheckBox("Start Nodes", objectName="startBox")
    configureBox = QCheckBox("Configure Nodes", objectName="configureBox")
    startBox.setChecked(True)
    configureBox.setChecked(True)

    verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

    submitButton = QPushButton("Submit", objectName="submitButton")
    submitButton.setFixedHeight(submitButtonHeight)

    vBoxContent = QVBoxLayout()
    for widget in [logo, actionLabel, actionBox, pathLabel, pathButton, projectLabel, projectBox, vmhostLabel, vmhostBox, startBox,
                   configureBox, verticalSpacer, submitButton]:
        if widget == verticalSpacer:
            vBoxContent.addItem(widget)
            continue
        vBoxContent.addWidget(widget)

    vBoxContent.setContentsMargins(30, 40, 30, 30)
    vBoxContent.setSpacing(10)

    vBoxCanvas.addWidget(whiteCanvas)
    whiteCanvas.setLayout(vBoxContent)

    pathButton.clicked.connect(lambda: openPath(actionBox, pathButton))
    submitButton.clicked.connect(
        lambda: checkSubmit(actionBox, pathButton, projectBox, vmhostBox, startBox, configureBox))
    actionBox.currentTextChanged.connect(lambda: checkAction(startBox, configureBox, actionBox, pathButton))
    startBox.stateChanged.connect(lambda: clickStart(startBox, configureBox))

    window.setLayout(vBoxCanvas)
    windowIcon = QIcon("./icon prototype.png")
    window.setWindowIcon(windowIcon)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
