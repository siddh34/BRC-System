from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QTabWidget, QDoubleSpinBox, QPushButton, QComboBox, QWidget, QSpinBox, QTableWidget, QFileDialog, QStatusBar, QSizeGrip, QFrame, QLineEdit, QPlainTextEdit, QTextEdit, QFileDialog

from PyQt5 import uic, QtGui

from PyQt5 import QtWidgets

from form import FormUI

from restoreForm import restoreFormUI

import sys, os, subprocess, datetime as dt, mysql.connector

class UI(QMainWindow):
    def __init__(self):
        """Constructor use only when you have to add components to UI which also has to functional at the same time"""
        super(UI, self).__init__()

        uic.loadUi("main.ui", self)

        # Path
        self.path = None

        # sql username / password
        self.sqlDatabaseName = None
        self.sqlUserPassword = None
        self.varList = []

        # Variable on page 1
        self.logs = self.findChild(QTableWidget,"Logs_4")
        self.saveDropDown = self.findChild(QComboBox,"SaveOn_4")
        self.DatabaseDropDown = self.findChild(QComboBox,"Database_4")
        self.backupButton = self.findChild(QPushButton,"Backup_4")
        self.recoverButton = self.findChild(QPushButton,"Recover_4")
        self.selectFolder = self.findChild(QPushButton,"SelectFolder")
        self.refreshButton = self.findChild(QPushButton,"RefreshButton")

        # Variable on page 2
        self.hostName = self.findChild(QLineEdit,"hostLineEdit_2")
        self.userName = self.findChild(QLineEdit,"userLineEdit_2")
        self.password = self.findChild(QLineEdit,"passwordLineEdit_2")
        self.database = self.findChild(QLineEdit,"databaseLineEdit_2")
        self.submitButton = self.findChild(QPushButton,"SubmitButton")
        self.queryButton = self.findChild(QPushButton,"Query_2")
        self.QueryBox =  self.findChild(QPlainTextEdit,"QueryBox_2")
        self.output = self.findChild(QPlainTextEdit,"Output_2")

        # Variable on page 3
        self.selectBackup = self.findChild(QPushButton,"SelectBackup_2")
        self.convert = self.findChild(QPushButton,"DatabaseC_2")
        self.save = self.findChild(QPushButton,"Save")
        self.preview = self.findChild(QPushButton,"Preview")
        self.PreviewBox = self.findChild(QTextEdit,"PreviewBox")

        # Assigning functions to buttons
        self.selectFolder.clicked.connect(self.selectFolderAction)
        self.refreshButton.clicked.connect(self.refreshLogAction)
        self.backupButton.clicked.connect(self.backup)
        self.recoverButton.clicked.connect(self.restore)

        self.show()

    # To show logs
    def displayLogs(self,directory):
        sql_files = []
        for root, dirs, files in os.walk("./Storage"):
            for file in files:  
                if file.endswith('.sql'):
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    modified_timestamp = os.path.getmtime(file_path)
                    modified_datetime = dt.datetime.fromtimestamp(modified_timestamp)
                    modified_str = modified_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    sql_files.append({
                        'name': file,
                        'size': size,
                        'modified': modified_str
                    })

        self.logs.setRowCount(len(sql_files))
        row = 0
        for data in sql_files:
            self.logs.setItem(row,0,QtWidgets.QTableWidgetItem(f"{row + 1}"))
            self.logs.setItem(row,1,QtWidgets.QTableWidgetItem(f"{data['name']}"))
            self.logs.setItem(row,2,QtWidgets.QTableWidgetItem(f"{data['size']}"))
            self.logs.setItem(row,3,QtWidgets.QTableWidgetItem(f"{data['modified']}"))
            row = row + 1

    # Provides us the folder in which backups will be stored
    def selectFolderAction(self):
        self.path = QFileDialog.getExistingDirectory(self, 'Select Folder')

        self.displayLogs(self.path)

    def refreshLogAction(self):
        if self.path != None:
            self.displayLogs(self.path)

    # To backup in specific directory
    def backup(self):
        self.checkPressed = False
        self.form = FormUI()
        self.form.my_signal.connect(self.receiveData)
    
    # To recieve data from from 
    def receiveData(self,data):
        self.varList = data
        print(self.varList)

        # taking username and password
        if(self.varList[2] == True):
            self.sqlDatabaseName = self.varList[0]
            self.sqlUserPassword = self.varList[1]
            print(self.sqlDatabaseName)
            print(self.sqlUserPassword)

            backupName = f"sqlBackup_{dt.datetime.now().strftime('%Y-%m-%d')}.sql"
            print(self.path)
            print(f'{self.path+"/"}{backupName}')
            if self.path != None:
                res = subprocess.run(['mysqldump', '-u', 'root', f'-p{self.sqlUserPassword}', f'{self.sqlDatabaseName}', '>', f'{self.path+"/"}{backupName}'], capture_output=True, text=True, shell=True)
                print(res.stderr)

    # To restore backup
    def restore(self):
        self.resForm = restoreFormUI()
        self.resForm.my_signal.connect(self.recieveRestoreData)

    def recieveRestoreData(self,data):
        print(data)
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

            # Build the command to restore the backup
            command = f"mysql -u {data[2]} -p{data[1]} {data[0]} < {selected_file}"

            # Run the command and capture the output
            result = subprocess.run(command, capture_output=True, text=True, shell=True)

            print(result.stderr)


if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = UI()
    app.exec_()