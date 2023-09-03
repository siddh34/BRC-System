from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton

from PyQt5.QtCore import pyqtSignal

from PyQt5 import uic, QtGui

from PyQt5 import QtWidgets

import sys

class restoreMongoformUI(QMainWindow):
    my_signal = pyqtSignal(list)

    def __init__(self):
        """Constructor use only when you have to add components to UI which also has to functional at the same time"""
        super(restoreMongoformUI, self).__init__()

        uic.loadUi("../design/RestoreMongoform.ui", self)

        #variables 
        self.DatabaseName = self.findChild(QLineEdit,"DatabaseNameLineEdit")
        self.hosts = self.findChild(QLineEdit,"hostLineEdit")
        self.port = self.findChild(QLineEdit,"portLineEdit")
        self.submitButton = self.findChild(QPushButton,"Submit")
        self.exitButton = self.findChild(QPushButton,"Exit")

        # Assigning the submit function to variable
        self.submitButton.clicked.connect(self.submit)
        self.exitButton.clicked.connect(self.close)

        self.show()

    def submit(self):
        dbName = self.DatabaseName.text()
        hostName = self.hosts.text()
        portName = int(self.port.text())
        self.my_signal.emit([dbName,hostName,portName])


if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = restoreMongoformUI()
    app.exec_()