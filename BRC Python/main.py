from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QComboBox, QTableWidget, QFileDialog, QLineEdit, QPlainTextEdit, QTextEdit, QFileDialog, QMessageBox, QTableWidgetItem

from PyQt5 import uic

from PyQt5 import QtWidgets, QtGui

from form import FormUI

from restoreForm import restoreFormUI

from UploadAWSForm import UploadAWSForm

from ceasarForm import ceasarFormUI

import sys, os, pandas as pd, subprocess, datetime as dt, mysql.connector, boto3

from cryptography.fernet import Fernet

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
        self.DatabaseDropDown = self.findChild(QComboBox,"Database_4")
        self.EncryptionDropDown = self.findChild(QComboBox,"EncryptionDropDown")
        self.backupButton = self.findChild(QPushButton,"Backup_4")
        self.recoverButton = self.findChild(QPushButton,"Recover_4")
        self.selectFolder = self.findChild(QPushButton,"SelectFolder")
        self.refreshButton = self.findChild(QPushButton,"RefreshButton")
        self.AWSUploadButton = self.findChild(QPushButton,"AWS_S3")
        self.Encrypt = self.findChild(QPushButton,"Encrypt")
        self.Decrypt = self.findChild(QPushButton,"Decrypt")

        # Variable on page 2
        self.hostName = self.findChild(QLineEdit,"hostLineEdit_2")
        self.userName = self.findChild(QLineEdit,"userLineEdit_2")
        self.password = self.findChild(QLineEdit,"passwordLineEdit_2")
        self.database = self.findChild(QLineEdit,"databaseLineEdit_2")
        self.submitButton = self.findChild(QPushButton,"SubmitButton")
        self.queryButton = self.findChild(QPushButton,"Query_2")
        self.QueryBox =  self.findChild(QPlainTextEdit,"QueryBox_2")
        self.output = self.findChild(QTableWidget,"Output_2")

        # Variable on page 3
        self.ConvertButton = self.findChild(QPushButton,"Convert")
        self.convertToCombo = self.findChild(QComboBox,"DatabaseC_2")
        self.saveButton = self.findChild(QPushButton,"Save")
        self.previewButton = self.findChild(QPushButton,"Preview")
        self.PreviewBox = self.findChild(QTextEdit,"PreviewBox")

        # Assigning functions to buttons
        self.selectFolder.clicked.connect(self.selectFolderAction)
        self.refreshButton.clicked.connect(self.refreshLogAction)
        self.backupButton.clicked.connect(self.backup)
        self.recoverButton.clicked.connect(self.restore)
        self.queryButton.clicked.connect(self.query)
        self.AWSUploadButton.clicked.connect(self.uploadToAWSS3)
        self.Encrypt.clicked.connect(self.encrypt)
        self.Decrypt.clicked.connect(self.decrypt)

        # variable for encryption
        self.Encryption_Selected_file = None

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
            self.logs.setItem(row,0,QtWidgets.QTableWidgetItem(f"{data['name']}"))
            self.logs.setItem(row,1,QtWidgets.QTableWidgetItem(f"{data['size']}"))
            self.logs.setItem(row,2,QtWidgets.QTableWidgetItem(f"{data['modified']}"))
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
    
    # To recieve data from form for backup 
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

    # function to restore backup
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

            # Run the command and capture the output

            result = subprocess.run(["mysql","-u","root",f"-p{data[1]}",f"{data[0]}",'-e', fr'SOURCE {selected_file}'], capture_output=True, text=True)

            print(result.stderr)

            print(result.stdout)

            print("Done!")

    # Used for encryption
    def encrypt(self):
        if self.EncryptionDropDown.currentIndex() == 0:
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
                self.Encryption_Selected_file = fileDialog.selectedFiles()[0]
                # Generate a random key
                key = Fernet.generate_key()

                filepath = "key.txt"

                # Checking wether key.txt exists
                if(os.path.isfile(filepath)):
                    i = 1
                    filepath = f"key{i}.txt"
                    while(os.path.isfile(filepath)):
                        i = i + 1
                        filepath = f"key{i}.txt"

                # Save the key to a file
                with open(filepath, "wb") as f:
                    f.write(key)

                # Load the key from a file
                with open(filepath, "rb") as f:
                    key = f.read()

                # Create a Fernet object
                fernet = Fernet(key)

                # opening the original file to encrypt
                with open(f'{self.Encryption_Selected_file}', 'rb') as file:
                    original = file.read()

                # encrypting the file
                encrypted = fernet.encrypt(original)

                # opening the file in write mode and
                # writing the encrypted data
                with open(f'{self.Encryption_Selected_file}', 'wb') as encrypted_file:
                    encrypted_file.write(encrypted)
        elif self.EncryptionDropDown.currentIndex() == 1:
            # Open the file dialog and set the options
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            # Set the file dialog properties
            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            fileDialog.setViewMode(QFileDialog.Detail)

            # Open the file dialog and get the selected file path
            if fileDialog.exec_() == QFileDialog.Accepted:
                file_selected = fileDialog.selectedFiles()[0]
                self.realFile = f"{file_selected}"
                self.getKeyForm()

    # Used for ceaesar encryption
    def caesar_encrypt(self,realText,step):
        outText = []
        cryptText = []
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        for eachLetter in realText:
            if eachLetter in uppercase:
                index = uppercase.index(eachLetter)
                crypting = (index + int(step)) % 26
                cryptText.append(crypting)
                newLetter = uppercase[crypting]
                outText.append(newLetter)
            elif eachLetter in lowercase:
                index = lowercase.index(eachLetter)
                crypting = (index + int(step)) % 26
                cryptText.append(crypting)
                newLetter = lowercase[crypting]
                outText.append(newLetter)
            elif eachLetter == " " or eachLetter == "\t" or eachLetter == "\n":
                outText.append(eachLetter)
        return outText

    # Redirects To ceasear form
    def getKeyForm(self):
        self.CeasarForm = ceasarFormUI()
        self.CeasarForm.my_signal.connect(self.getKey)

    # Does the encryption
    def getKey(self,data):
        step = data[0]
        with open(self.realFile, 'r') as f:
            text = f.read()
        code = self.caesar_encrypt(text,step)
        with open(self.realFile + ".encrypted", 'w') as f:
            for i in code:
                f.write(i)
        print("The Encrypted Message is saved in", self.realFile + ".encrypted")

    # Used for decryption
    def decrypt(self):
        if self.EncryptionDropDown.currentIndex() == 0:
            # Open the file dialog and set the options
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            # Set the file dialog properties
            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            fileDialog.setNameFilter("Text (*.txt)")
            fileDialog.setViewMode(QFileDialog.Detail)

            fileDialog2 = QFileDialog()
            fileDialog2.setFileMode(QFileDialog.AnyFile)
            fileDialog2.setViewMode(QFileDialog.Detail)

            # Open the file dialog and get the selected file path
            if fileDialog.exec_() == QFileDialog.Accepted and fileDialog2.exec_() == QFileDialog.Accepted:
                key_file = fileDialog.selectedFiles()[0]
                encrypted_file = fileDialog2.selectedFiles()[0]
                
                with open(f"{key_file}", "rb") as f:
                    key = f.read()

                # Create a Fernet object
                fernet = Fernet(key)

                # opening the encrypted file
                with open(f'{encrypted_file}', 'rb') as enc_file:
                    encrypted = enc_file.read()

                # decrypting the file
                decrypted = fernet.decrypt(encrypted)

                # opening the file in write mode and
                # writing the decrypted data
                with open(f'{encrypted_file}', 'wb') as dec_file:
                    dec_file.write(decrypted)
        elif self.EncryptionDropDown.currentIndex() == 1:
            pass

    # Used for ceaesar decryption
    def caesar_decrypt(realText, step):
        outText = []
        cryptText = []
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        for eachLetter in realText:
            if eachLetter in uppercase:
                index = uppercase.index(eachLetter)
                crypting = (index - int(step)) % 26
                cryptText.append(crypting)
                newLetter = uppercase[crypting]
                outText.append(newLetter)
            elif eachLetter in lowercase:
                index = lowercase.index(eachLetter)
                crypting = (index - int(step)) % 26
                cryptText.append(crypting)
                newLetter = lowercase[crypting]
                outText.append(newLetter)
            elif eachLetter == " " or eachLetter == "\t" or eachLetter == "\n":
                outText.append(eachLetter)
        return outText

    # Query the database
    def query(self):
        msgBox = QMessageBox()
        if self.hostName.text() == "" or self.password.text() == "" or self.database.text() == "" or self.userName.text() == "":
            msgBox.setText("Please Enter the respective fields.")
            msgBox.exec()
        else:
            mydatabase = mysql.connector.connect(
                host=f"{self.hostName.text()}",
                user=f"{self.userName.text()}",
                password=f"{self.password.text()}",
                database=f"{self.database.text()}"
            )

            try: 
                cursor = self.QueryBox.textCursor()
                cursor.select(QtGui.QTextCursor.BlockUnderCursor)
                query = cursor.selectedText()

                df = pd.read_sql_query(f'{query}', mydatabase)

                self.output.setColumnCount(len(df.columns))
                self.output.setRowCount(len(df))

                headers = df.columns.tolist()
                self.output.setHorizontalHeaderLabels(headers)

                for i, row in enumerate(df.values):
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.output.setItem(i, j, item)
            except Exception:
                msgBox.setText("Something went wrong!")
                msgBox.exec()
            # TODO: Explore & add various types of exceptions

    # Uploads file to aws
    def uploadToAWSS3(self):
        self.AWS = UploadAWSForm()
        self.AWS.my_signal.connect(self.receiveToUploadAWS)

    # Recieve information for uploading to S3
    def receiveToUploadAWS(self,data):
        print(data)
        ACCESS_KEY_ID = f"{data[0]}"
        SECRET_ACCESS_KEY = f"{data[1]}"

        # Create a Boto3 client
        s3 = boto3.client("s3", aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)

        # Upload a file to S3
        file_path = fr"{data[2]}"
        bucket_name = f"{data[3]}"
        object_key = f"backupsql_{dt.datetime.now().strftime('%Y-%m-%d')}"

        s3.upload_file(file_path, bucket_name, object_key)

        # Check if the file is uploaded successfully
        response = s3.head_object(Bucket=bucket_name, Key=object_key)

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print("File uploaded successfully")
        else:
            print("File upload failed")

    # Convert function
    def convert(self):
        pass

if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = UI()
    app.exec_()