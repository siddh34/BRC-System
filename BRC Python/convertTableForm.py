from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton

from PyQt5.QtCore import pyqtSignal

from PyQt5 import uic, QtGui

from PyQt5 import QtWidgets

import sys

class convertFormUI(QMainWindow):
    my_signal = pyqtSignal(list)

    def __init__(self):
        """Constructor use only when you have to add components to UI which also has to functional at the same time"""
        super(convertFormUI, self).__init__()

        uic.loadUi("convertTable.ui", self)

        #variables 
        self.DatabaseName = self.findChild(QLineEdit,"DatabaseNameLineEdit")
        self.password = self.findChild(QLineEdit,"passwordLineEdit")
        self.hosts = self.findChild(QLineEdit,"hostsLineEdit")
        self.user = self.findChild(QLineEdit,"userLineEdit")
        self.mongoClientName = self.findChild(QLineEdit,"mongoClientNameLineEdit")
        self.collectionName = self.findChild(QLineEdit,"collectionNameLineEdit")
        self.sQLTabelName = self.findChild(QLineEdit,"sQLTabelNameLineEdit")
        self.submitButton = self.findChild(QPushButton,"Submit")
        self.exitButton = self.findChild(QPushButton,"Exit")

        # Assigning the submit function to variable
        self.submitButton.clicked.connect(self.submit)
        self.exitButton.clicked.connect(self.close)

        self.show()

    def submit(self):
        self.DatabaseNameText = self.DatabaseName.text()
        self.passwordText = self.password.text()
        self.hostsText = self.hosts.text()
        self.userText = self.user.text()
        self.mongoClientNameText = self.mongoClientName.text()
        self.collectionNameText = self.collectionName.text()
        self.sQLTabelNameText = self.sQLTabelName.text()
        self.my_signal.emit([self.DatabaseNameText,self.passwordText,self.hostsText,self.userText,self.mongoClientNameText,self.collectionNameText,self.sQLTabelNameText])


if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = convertFormUI()
    app.exec_()