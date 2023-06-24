from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton

from PyQt5.QtCore import pyqtSignal

from PyQt5 import uic, QtGui

from PyQt5 import QtWidgets

import sys

class mongoBackUpFormUI(QMainWindow):
    my_signal = pyqtSignal(list)

    def __init__(self):
        """Constructor use only when you have to add components to UI which also has to functional at the same time"""
        super(mongoBackUpFormUI, self).__init__()

        uic.loadUi("mongoBackupForm.ui", self)

        #variables 
        self.collections = self.findChild(QLineEdit,"CollectionLineEdit")
        self.DatabaseName = self.findChild(QLineEdit,"DatabaseNameLineEdit")
        self.submitButton = self.findChild(QPushButton,"Submit")
        self.exitButton = self.findChild(QPushButton,"Exit")
        self.subClicked = False

        # Assigning the submit function to variable
        self.submitButton.clicked.connect(self.submit)
        self.exitButton.clicked.connect(self.close)

        self.show()

    def submit(self):
        self.DatabaseName_2 = self.DatabaseName.text()
        self.col = self.collections.text()
        self.my_signal.emit([self.DatabaseName_2,self.col])

if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = mongoBackUpFormUI()
    app.exec_()