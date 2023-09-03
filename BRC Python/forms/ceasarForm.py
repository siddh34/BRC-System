from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton

from PyQt5.QtCore import pyqtSignal

from PyQt5 import uic, QtGui

from PyQt5 import QtWidgets

import sys

class ceasarFormUI(QMainWindow):
    my_signal = pyqtSignal(list)

    def __init__(self):
        """Constructor use only when you have to add components to UI which also has to functional at the same time"""
        super(ceasarFormUI, self).__init__()

        uic.loadUi("../design/ceasarForm.ui", self)

        #variables 
        self.key = self.findChild(QLineEdit,"pass")
        self.submitButton = self.findChild(QPushButton,"Submit")
        self.exitButton = self.findChild(QPushButton,"Exit")

        # Assigning the submit function to variable
        self.submitButton.clicked.connect(self.submit)
        self.exitButton.clicked.connect(self.close)

        self.show()

    def submit(self):
        self.keyText = self.key.text()
        self.my_signal.emit([self.keyText])


if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = ceasarFormUI()
    app.exec_()