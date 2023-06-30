from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QComboBox, QTableWidget, QFileDialog, QLineEdit, QPlainTextEdit, QTextEdit, QFileDialog, QMessageBox, QTableWidgetItem, QProgressBar

from PyQt5 import uic

from PyQt5 import QtWidgets, QtGui

from form import FormUI

# from PyQt5.QtCore import QBasicTimer

from restoreForm import restoreFormUI

from UploadAWSForm import UploadAWSForm

from ceasarForm import ceasarFormUI

from convertTableForm import convertFormUI

from mongoBackupForm import mongoBackUpFormUI

from RestoreMongoform import restoreMongoformUI

import sys, os, pandas as pd, subprocess, datetime as dt, mysql.connector, boto3, json

from bson import json_util

from cryptography.fernet import Fernet

from pymongo import MongoClient

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
        self.fields = self.findChild(QTextEdit,"schemaData")
        self.progressBar = self.findChild(QProgressBar,"progressBar")

        # Assigning functions to buttons
        self.selectFolder.clicked.connect(self.selectFolderAction)
        self.refreshButton.clicked.connect(self.refreshLogAction)
        self.backupButton.clicked.connect(self.backup)
        self.recoverButton.clicked.connect(self.restore)
        self.queryButton.clicked.connect(self.query)
        self.AWSUploadButton.clicked.connect(self.uploadToAWSS3)
        self.Encrypt.clicked.connect(self.encrypt)
        self.Decrypt.clicked.connect(self.decrypt)
        self.ConvertButton.clicked.connect(self.convertForm)
        self.previewButton.clicked.connect(self.previewConvert)
        self.saveButton.clicked.connect(self.saveConvert)

        # These variables are for QProgressBar
        # self.timer = QBasicTimer()
        # self.step = 0
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

        # variable for encryption
        self.Encryption_Selected_file = None

        self.show()

    # To show logs
    def displayLogs(self,directory):
        if self.DatabaseDropDown.currentIndex() == 0:
            sql_files = []
            for root, dirs, files in os.walk(directory):
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

            # Updating the table

            self.logs.setRowCount(len(sql_files))
            row = 0
            for data in sql_files:
                self.logs.setItem(row,0,QtWidgets.QTableWidgetItem(f"{data['name']}"))
                self.logs.setItem(row,1,QtWidgets.QTableWidgetItem(f"{data['size']}"))
                self.logs.setItem(row,2,QtWidgets.QTableWidgetItem(f"{data['modified']}"))
                row = row + 1

        elif self.DatabaseDropDown.currentIndex() == 1:
            directories = []
            for entry in os.scandir(directory):
                if entry.is_dir():
                    subdirectory = entry.path
                    size = os.path.getsize(subdirectory)
                    modified_timestamp = os.path.getmtime(subdirectory)
                    modified_datetime = dt.datetime.fromtimestamp(modified_timestamp)
                    modified_str = modified_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    directories.append({
                        'name': entry.name,
                        'size': size,
                        'modified': modified_str
                    })
            self.logs.setRowCount(len(directories))
            row = 0
            for data in directories:
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
        if self.DatabaseDropDown.currentIndex() == 0:
            self.checkPressed = False
            self.form = FormUI()
            self.form.my_signal.connect(self.receiveData)
        elif self.DatabaseDropDown.currentIndex() == 1:
            self.form = mongoBackUpFormUI()
            self.form.my_signal.connect(self.receiveData)

    # To recieve data from form for backup 
    def receiveData(self,data):
        if self.DatabaseDropDown.currentIndex() == 0:
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
        elif self.DatabaseDropDown.currentIndex() == 1:
            print(data)
            # Get the path
            curr = QFileDialog.getExistingDirectory(self, 'Select Folder')

            mongoBackupName = f"mongoBackup_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

            # Path
            path = os.path.join(curr, mongoBackupName)

            # make a new directory
            os.mkdir(path)

            command = ["mongodump",  "--db", data[0], "--collection", data[1], "--out", path]

            subprocess.run(command)


    # To restore backup
    def restore(self):
        if self.DatabaseDropDown.currentIndex() == 0:
            self.resForm = restoreFormUI()
            self.resForm.my_signal.connect(self.recieveRestoreData)
        elif self.DatabaseDropDown.currentIndex() == 1:
            self.resForm = restoreMongoformUI()
            self.resForm.my_signal.connect(self.recieveRestoreData)

    # function to restore backup
    def recieveRestoreData(self,data):
        if self.DatabaseDropDown.currentIndex() == 0:
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
        elif self.DatabaseDropDown.currentIndex() == 1:
            print(data)
            # Open the file dialog and set the options
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            # Set the file dialog properties
            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.Directory)  # Set the file mode to select directories
            fileDialog.setViewMode(QFileDialog.Detail)
            fileDialog.setViewMode(QFileDialog.Detail)

            # Open the file dialog and get the selected file path
            if fileDialog.exec_() == QFileDialog.Accepted:
                selected_file = fileDialog.selectedFiles()[0]
                print("Selected file:", selected_file)
                selected_file = fr'"{selected_file}"'

                command = fr"mongorestore --host {data[1]} --port {data[2]} --db {data[0]} {selected_file}"

                try:
                    subprocess.run(command, shell=True, check=True)
                    print("MongoDB restore completed successfully!")
                except subprocess.CalledProcessError as e:
                    print(f"Error occurred during MongoDB restore: {e}")

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
                self.getKeyFormDecrypt()

    def getKeyFormDecrypt(self):
        self.CeasarForm = ceasarFormUI()
        self.CeasarForm.my_signal.connect(self.getKeyDecrypt)

    # Does the encryption
    def getKeyDecrypt(self,data):
        step = data[0]
        with open(self.realFile, 'r') as f:
            text = f.read()
        code = self.caesar_decrypt(text,step)
        with open(self.realFile + ".decrypted", 'w') as f:
            for i in code:
                f.write(i)
        print("The Decrypted Message is saved in", self.realFile + ".decrypted")

    # Used for ceaesar decryption
    def caesar_decrypt(self,realText, step):
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
            try: 
                mydatabase = mysql.connector.connect(
                    host=f"{self.hostName.text()}",
                    user=f"{self.userName.text()}",
                    password=f"{self.password.text()}",
                    database=f"{self.database.text()}"
                )
                cursor = self.QueryBox.textCursor()
                cursor.select(QtGui.QTextCursor.BlockUnderCursor)
                query = cursor.selectedText()

                df = pd.read_sql_query(f'{query}', mydatabase)

                # TODO: convert df to actual df to get a savable xlxs

                self.output.setColumnCount(len(df.columns))
                self.output.setRowCount(len(df))

                headers = df.columns.tolist()
                self.output.setHorizontalHeaderLabels(headers)

                for i, row in enumerate(df.values):
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.output.setItem(i, j, item)
            except Exception as e:
                msgBox.setText(f"{str(e)}")
                msgBox.exec()

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

    # pulls out the convert form
    def convertForm(self):
        self.ConvertForm = convertFormUI()
        self.ConvertForm.my_signal.connect(self.convert)

    # Convert function
    def convert(self,data):
        # split the fields
        self.fieldsLines = self.fields.toPlainText().split(" ")

        self.progressBar.setValue(10)

        # saving the datalist
        self.dataList = data

        # Connect to the SQL database
        sql_connection = mysql.connector.connect(
            host=f'{data[2]}',
            user=f'{data[3]}',
            password=f'{data[1]}',
            database=f'{data[0]}'
        )

        self.progressBar.setValue(20)

        # Connect to the MongoDB database
        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client[f'{data[4]}']
        mongo_collection = mongo_db[f'{data[5]}']

        # Retrieve data from the SQL table
        sql_cursor = sql_connection.cursor()
        sql_cursor.execute(f'SELECT * FROM {data[6]}')
        sql_data = sql_cursor.fetchall()

        self.progressBar.setValue(45)

        # Transform and insert data into MongoDB collection
        j = 0
        for row in sql_data:
            doc = {}
            j += 5
            for i, myfield in enumerate(self.fieldsLines):
                doc[myfield] = row[i]
                self.progressBar.setValue(45 + j)

            mongo_collection.insert_one(doc)

        self.progressBar.setValue(100)

    # Save Function for convert screen
    def saveConvert(self):
        msgBox = QMessageBox()
        try:
            # Connect to the MongoDB server
            client = MongoClient('mongodb://localhost:27017/')

            # Access the MongoDB database and collection
            db = client[f'{self.dataList[4]}']
            collection = db[f'{self.dataList[5]}']

            # Retrieve the documents from the collection
            documents = collection.find()

            # Convert the documents to a list of dictionaries
            document_list = [doc for doc in documents]

            # Serialize the documents to JSON using json_util
            json_data = json.dumps(document_list, default=json_util.default, indent=4)

            filepath = "output.json"

            # Checking wether output file exists
            if(os.path.isfile(filepath)):
                i = 1
                filepath = f"output{i}.json"
                while(os.path.isfile(filepath)):
                    i = i + 1
                    filepath = f"output{i}.json"

            # Save the JSON data to a file
            with open(f'{filepath}', 'w') as file:
                file.write(json_data)

            # Close the MongoDB connection
            client.close()
        except Exception as e:
            msgBox.setText(f"Please use convert first")
            msgBox.exec()

    # Preview Function for convert screen
    def previewConvert(self):
        msgBox = QMessageBox()
        try:
            client = MongoClient('mongodb://localhost:27017/')

            # Access the MongoDB database and collection
            db = client[f'{self.dataList[4]}']
            collection = db[f'{self.dataList[5]}']

            # Retrieve the documents from the collection
            documents = collection.find()

            # Convert the documents to a list of dictionaries
            document_list = [doc for doc in documents]

            # Serialize the documents to JSON using json_util
            json_data = json.dumps(document_list, default=json_util.default, indent=4)

            self.PreviewBox.setPlainText(json_data)

            # close connection
            client.close()
        except Exception as e:
            msgBox.setText(f"Please use convert first")
            msgBox.exec()

if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = UI()
    app.exec_()
