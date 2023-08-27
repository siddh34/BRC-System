from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton

from PyQt5.QtCore import pyqtSignal

from PyQt5 import uic, QtGui

from PyQt5 import QtWidgets

import sys

class FormUI(QMainWindow):
    my_signal = pyqtSignal(list)

    def __init__(self):
        """Constructor use only when you have to add components to UI which also has to functional at the same time"""
        super(FormUI, self).__init__()

        uic.loadUi("./design/form.ui", self)

        #variables 
        self.password = self.findChild(QLineEdit,"passwordLineEdit")
        self.Databasename = self.findChild(QLineEdit,"DatabaseNameLineEdit")
        self.submitButton = self.findChild(QPushButton,"Submit")
        self.exitButton = self.findChild(QPushButton,"Exit")
        self.subClicked = False

        # Assigning the submit function to variable
        self.submitButton.clicked.connect(self.submit)
        self.exitButton.clicked.connect(self.close)

        self.show()

    def submit(self):
        self.Databasename_2 = self.Databasename.text()
        self.pas = self.password.text()
        self.subClicked = True
        self.my_signal.emit([self.Databasename_2,self.pas,self.subClicked])


if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = FormUI()
    app.exec_()