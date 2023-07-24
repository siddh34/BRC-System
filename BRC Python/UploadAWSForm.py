from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QFileDialog

from PyQt5.QtCore import pyqtSignal

from PyQt5 import uic, QtGui

from PyQt5 import QtWidgets

import sys

class UploadAWSForm(QMainWindow):
    my_signal = pyqtSignal(list)

    def __init__(self):
        """Constructor use only when you have to add components to UI which also has to functional at the same time"""
        super(UploadAWSForm, self).__init__()

        uic.loadUi("UploadAWSForm.ui", self)

        #variables 
        self.accessKey = self.findChild(QLineEdit,"accessKeyIDLineEdit")
        self.secretAccessKey = self.findChild(QLineEdit,"secretAccessKeyLineEdit")
        self.bucketName = self.findChild(QLineEdit,"bucketNameLineEdit")
        self.submitButton = self.findChild(QPushButton,"Submit")
        self.exitButton = self.findChild(QPushButton,"Exit")

        # Assigning the submit function to variable
        self.submitButton.clicked.connect(self.submit)
        self.exitButton.clicked.connect(self.close)

        self.show()

    def submit(self):
        # Open the file dialog and set the options
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        options |= QFileDialog.DontResolveSymlinks

        # Set the file dialog properties
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.AnyFile)
        fileDialog.setNameFilter("SQL files (*.sql)")
        fileDialog.setViewMode(QFileDialog.Detail)

        # Open the file dialog and get the selected file path
        if fileDialog.exec_() == QFileDialog.Accepted:
            selected_file = fileDialog.selectedFiles()[0]
            print("Selected file:", selected_file)
            self.path = selected_file

        self.accessKeyID = self.accessKey.text()
        self.secretAccessKeyID = self.secretAccessKey.text()
        self.bucket = self.bucketName.text()
        self.my_signal.emit([self.accessKeyID,self.secretAccessKeyID,self.path,self.bucket])


if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = UploadAWSForm()
    app.exec_()