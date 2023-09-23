from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QComboBox, QTableWidget, QFileDialog, QLineEdit, QPlainTextEdit, QTextEdit, QFileDialog, QMessageBox, QTableWidgetItem, QProgressBar, QLabel

from PyQt5 import uic

from PyQt5 import QtWidgets, QtGui

from forms.form import FormUI

from forms.restoreForm import restoreFormUI

from forms.UploadAWSForm import UploadAWSForm

from forms.ceasarForm import ceasarFormUI

from forms.convertTableForm import convertFormUI

from forms.mongoBackupForm import mongoBackUpFormUI

from forms.RestoreMongoform import restoreMongoformUI

import sys, os, pandas as pd, subprocess, datetime as dt, mysql.connector, boto3, json

from bson import json_util

from cryptography.fernet import Fernet

from pymongo import MongoClient

from ecies import encrypt, decrypt

from ecies.utils import generate_key

class UI(QMainWindow):
    def __init__(self):
        """Constructor use only when you have to add components to UI which also has to functional at the same time"""
        super(UI, self).__init__()

        uic.loadUi("./design/main.ui", self)

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
        self.hostLabel = self.findChild(QLabel,"hostLabel_2")
        self.userName = self.findChild(QLineEdit,"userLineEdit_2")
        self.userNameLabel = self.findChild(QLabel,"userLabel_2")
        self.password = self.findChild(QLineEdit,"passwordLineEdit_2")
        self.passLabel = self.findChild(QLabel,"passwordLabel_2")
        self.database = self.findChild(QLineEdit,"databaseLineEdit_2")
        self.dataLabel = self.findChild(QLabel,"databaseLabel_2")
        self.submitButton = self.findChild(QPushButton,"SubmitButton")
        self.queryButton = self.findChild(QPushButton,"Query_2")
        self.QueryBox =  self.findChild(QPlainTextEdit,"QueryBox_2")
        self.QueryOutputBox2 =  self.findChild(QPlainTextEdit,"QueryOutput2")
        self.output = self.findChild(QTableWidget,"Output_2")
        self.changingLabel = self.findChild(QLabel,"variableLabel")
        self.screen2DropDown = self.findChild(QComboBox,"DatabaseSelectTab2")

        # Variable on page 3
        self.ConvertButton = self.findChild(QPushButton,"Convert")
        self.convertToCombo = self.findChild(QComboBox,"DatabaseC_2")
        self.saveButton = self.findChild(QPushButton,"Save")
        self.previewButton = self.findChild(QPushButton,"Preview")
        self.PreviewBox = self.findChild(QTextEdit,"PreviewBox")
        self.fields = self.findChild(QTextEdit,"schemaData")
        self.progressBar = self.findChild(QProgressBar,"progressBar")
        self.screen3DropDown = self.findChild(QComboBox,"DatabaseC_2")
        self.convertSQLTable = self.findChild(QTableWidget,"convertSQLTable")
        self.FromToText = self.findChild(QLabel,"FromTo")
        # self.ConvertMongoTable = self.findChild(QTableWidget,"MongoToSQL")

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
        self.screen2DropDown.currentIndexChanged.connect(self.changeDataOnSecondScreen)
        self.screen2DropDown.currentIndexChanged.connect(self.changeDataOnSecondScreen)
        self.screen3DropDown.currentIndexChanged.connect(self.changeWidgetsOnThirdScreen)

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

        self.Encryption_Selected_file = None

        self.QueryOutputBox2.hide()
        self.convertSQLTable.hide()
        # self.ConvertMongoTable.hide()

        # create a msg box
        self.msgBox = QMessageBox()
        try:
            subprocess.run(["mysqldump", "--version"], check=True)
        except FileNotFoundError:
            self.msgBox.setText("MySQL not installed!Please install MySQL")
            self.msgBox.exec()

        try:
            subprocess.run(["mongo", "--version"], check=True)
        except FileNotFoundError:
            self.msgBox.setText("Mongodb not installed!\nPlease install MongoDB and try again")
            self.msgBox.exec()

        self.show()

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

    def selectFolderAction(self):
        self.path = QFileDialog.getExistingDirectory(self, 'Select Folder')

        self.displayLogs(self.path)

    def refreshLogAction(self):
        if self.path != None:
            self.displayLogs(self.path)

    def backup(self):
        if self.DatabaseDropDown.currentIndex() == 0:
            self.checkPressed = False
            self.form = FormUI()
            self.form.my_signal.connect(self.receiveData)
        elif self.DatabaseDropDown.currentIndex() == 1:
            self.form = mongoBackUpFormUI()
            self.form.my_signal.connect(self.receiveData)

    def receiveData(self,data):
        if self.DatabaseDropDown.currentIndex() == 0:
            self.varList = data
            print(self.varList)

            if(self.varList[2] == True):
                self.sqlDatabaseName = self.varList[0]
                self.sqlUserPassword = self.varList[1]
                print(self.sqlDatabaseName)
                print(self.sqlUserPassword)

                backupName = f"sqlBackup_{dt.datetime.now().strftime('%Y-%m-%d')}.sql"
                print(self.path)
                print(f'{self.path+"/"}{backupName}')

                outpath = f"{self.path}/{backupName}"

                if self.path != None:

                    mysqldump_command = [
                        "mysqldump",
                        "-u",
                        "root",
                        f'-p{self.sqlUserPassword}',
                        "-d",
                        f'{self.sqlDatabaseName}',
                    ]

                    with open(outpath, "w") as outfile:
                        try:
                            subprocess.run(mysqldump_command, text=True, stdout=outfile)
                            print("Database dump completed successfully.")
                        except subprocess.CalledProcessError as e:
                            print(f"Error occurred during database dump: {e}")

        elif self.DatabaseDropDown.currentIndex() == 1:
            curr = QFileDialog.getExistingDirectory(self, 'Select Folder')

            mongoBackupName = f"mongoBackup_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

            path = os.path.join(curr, mongoBackupName)

            os.mkdir(path)

            command = ["mongodump",  "--db", data[0], "--collection", data[1], "--out", path]

            subprocess.run(command)

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
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            fileDialog.setNameFilter("SQL files (*.sql)")
            fileDialog.setViewMode(QFileDialog.Detail)

            if fileDialog.exec_() == QFileDialog.Accepted:
                selected_file = fileDialog.selectedFiles()[0]
                print("Selected file:", selected_file)


                result = subprocess.run(["mysql","-u","root",f"-p{data[1]}",f"{data[0]}",'-e', fr'SOURCE {selected_file}'], capture_output=True, text=True)

                print(result.stderr)

                print(result.stdout)

                print("Done!")
        elif self.DatabaseDropDown.currentIndex() == 1:
            print(data)
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.Directory)  
            fileDialog.setViewMode(QFileDialog.Detail)
            fileDialog.setViewMode(QFileDialog.Detail)

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

    def encrypt(self):
        if self.EncryptionDropDown.currentIndex() == 0:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            fileDialog.setNameFilter("SQL/BSON files (*.sql, *.bson)")
            fileDialog.setViewMode(QFileDialog.Detail)

            if fileDialog.exec_() == QFileDialog.Accepted:
                self.Encryption_Selected_file = fileDialog.selectedFiles()[0]
                key = Fernet.generate_key()

                filepath = "key.txt"

                if(os.path.isfile(filepath)):
                    i = 1
                    filepath = f"key{i}.txt"
                    while(os.path.isfile(filepath)):
                        i = i + 1
                        filepath = f"key{i}.txt"

                with open(filepath, "wb") as f:
                    f.write(key)

                with open(filepath, "rb") as f:
                    key = f.read()

                fernet = Fernet(key)

                with open(f'{self.Encryption_Selected_file}', 'rb') as file:
                    original = file.read()

                encrypted = fernet.encrypt(original)

                with open(f'{self.Encryption_Selected_file}', 'wb') as encrypted_file:
                    encrypted_file.write(encrypted)
        elif self.EncryptionDropDown.currentIndex() == 1:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            fileDialog.setViewMode(QFileDialog.Detail)

            if fileDialog.exec_() == QFileDialog.Accepted:
                file_selected = fileDialog.selectedFiles()[0]
                self.realFile = f"{file_selected}"
                self.getKeyForm()
        elif self.EncryptionDropDown.currentIndex() == 2:
            self.msgBox.setText("This generates ecc.txt file make sure that you have already decrypted the file which was first encrypted using this file or copy paste the ecc.txt into some other file and then continue")
            self.msgBox.exec()
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            fileDialog.setViewMode(QFileDialog.Detail)

            self.realFile = None
            if fileDialog.exec_() == QFileDialog.Accepted:
                file_selected = fileDialog.selectedFiles()[0]
                self.realFile = f"{file_selected}"

            if self.realFile == None:
                self.msgBox.setText("Please select a file")
                self.msgBox.exec()

            data = None
            with open(self.realFile, "rb") as f:
                data = f.read()
            
            if data == None:
                self.msgBox.setText("File may be an empty file")
                self.msgBox.exec()

            key_pair = generate_key()
            public_key = key_pair.public_key.format(True)
            secret_key = key_pair.secret

            with open("ecc.txt", "wb") as f:
                f.write(b"Public Key:")
                f.write(public_key)
                f.write(b"Secret Key:")
                f.write(secret_key)

            encrypted = encrypt(public_key, data)

            with open(self.realFile, "wb") as f:
                f.write(encrypted)

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

    def getKeyForm(self):
        self.CeasarForm = ceasarFormUI()
        self.CeasarForm.my_signal.connect(self.getKey)

    def getKey(self,data):
        step = data[0]
        with open(self.realFile, 'r') as f:
            text = f.read()
        code = self.caesar_encrypt(text,step)
        with open(self.realFile + ".encrypted", 'w') as f:
            for i in code:
                f.write(i)
        print("The Encrypted Message is saved in", self.realFile + ".encrypted")

    def decrypt(self):
        if self.EncryptionDropDown.currentIndex() == 0:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            fileDialog.setViewMode(QFileDialog.Detail)

            fileDialog2 = QFileDialog()
            fileDialog2.setFileMode(QFileDialog.AnyFile)
            fileDialog2.setViewMode(QFileDialog.Detail)

            if fileDialog.exec_() == QFileDialog.Accepted and fileDialog2.exec_() == QFileDialog.Accepted:
                key_file = fileDialog.selectedFiles()[0]
                encrypted_file = fileDialog2.selectedFiles()[0]
                
                with open(f"{key_file}", "rb") as f:
                    key = f.read()

                fernet = Fernet(key)

                with open(f'{encrypted_file}', 'rb') as enc_file:
                    encrypted = enc_file.read()

                decrypted = fernet.decrypt(encrypted)

                with open(f'{encrypted_file}', 'wb') as dec_file:
                    dec_file.write(decrypted)
        elif self.EncryptionDropDown.currentIndex() == 1:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            fileDialog.setViewMode(QFileDialog.Detail)

            if fileDialog.exec_() == QFileDialog.Accepted:
                file_selected = fileDialog.selectedFiles()[0]
                self.realFile = f"{file_selected}"
                self.getKeyFormDecrypt()
        elif self.EncryptionDropDown.currentIndex() == 2:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.ShowDirsOnly
            options |= QFileDialog.DontResolveSymlinks

            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            fileDialog.setViewMode(QFileDialog.Detail)
            
            self.realFile = None
            if fileDialog.exec_() == QFileDialog.Accepted:
                file_selected = fileDialog.selectedFiles()[0]
                self.realFile = f"{file_selected}"

            if self.realFile == None:
                self.msgBox.setText("Please select a file")
                self.msgBox.exec()

            encrypted_data = None

            with open(self.realFile, "rb") as f:
                encrypted_data = f.read()

            with open("ecc.txt", "rb") as f:
                content = f.read()

            secret_key = None
            parts = content.split(b"Secret Key:")
            if len(parts) > 1:
                secret_key = parts[1].strip()

            decrypted_data = decrypt(secret_key, encrypted_data)

            with open(self.realFile, "wb") as f:
                f.write(decrypted_data)
            
    def getKeyFormDecrypt(self):
        self.CeasarForm = ceasarFormUI()
        self.CeasarForm.my_signal.connect(self.getKeyDecrypt)

    def getKeyDecrypt(self,data):
        step = data[0]
        with open(self.realFile, 'r') as f:
            text = f.read()
        code = self.caesar_decrypt(text,step)
        with open(self.realFile + ".decrypted", 'w') as f:
            for i in code:
                f.write(i)
        print("The Decrypted Message is saved in", self.realFile + ".decrypted")

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

    def changeDataOnSecondScreen(self):
        if self.screen2DropDown.currentIndex() == 0:
            self.changingLabel.setText("Note: For SQL Query, you can direct write the Queries")

            self.hostLabel.setText("Host")
            self.userNameLabel.setText("User")
            self.password.setVisible(True)
            self.database.setVisible(True)
            self.dataLabel.setVisible(True)
            self.passLabel.setVisible(True)
            self.output.setVisible(True)

            self.QueryOutputBox2.hide()

        elif self.screen2DropDown.currentIndex() == 1:
            self.changingLabel.setText("Note: For mongo enter values {field, query} then press query")

            self.hostLabel.setText("Database")
            self.userNameLabel.setText("Collection")

            self.password.hide()
            self.database.hide()
            self.dataLabel.hide()
            self.passLabel.hide()
            self.output.hide()

            self.QueryOutputBox2.setVisible(True)

    def query(self):
        if self.screen2DropDown.currentIndex() == 0:
            self.output.clearContents()
            if self.hostName.text() == "" or self.password.text() == "" or self.database.text() == "" or self.userName.text() == "":
                self.msgBox.setText("Please Enter the respective fields.")
                self.msgBox.exec()
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
                    self.msgBox.setText(f"{str(e)}")
                    self.msgBox.exec()
        elif self.screen2DropDown.currentIndex() == 1:
            self.QueryOutputBox2.clear()
            client = MongoClient("mongodb://localhost:27017")
            cursor = self.QueryBox.textCursor()
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            query = cursor.selectedText()

            db = client[f"{self.hostName.text()}"]
            collection = db[f"{self.userName.text()}"]
            try:
                if query == "":
                    result = collection.find()

                    for document in result:
                        print(document)
                        self.QueryOutputBox2.appendPlainText(f"{document}\n")
                else:
                    pair = query.split()
                    # TODO: Generate this randomly as if more pairs are their
                    query = {f"{pair[0]}": f"{pair[1]}"}

                    result = collection.find(query)

                    print(result)

                    for document in result:
                        print(document)
                        self.QueryOutputBox2.appendPlainText(f"{document}\n")

            except Exception as e:
                self.msgBox.setText(f"{str(e)}")
                self.msgBox.exec()

    def uploadToAWSS3(self):
        self.AWS = UploadAWSForm()
        self.AWS.my_signal.connect(self.receiveToUploadAWS)

    def receiveToUploadAWS(self,data):
        print(data)
        ACCESS_KEY_ID = f"{data[0]}"
        SECRET_ACCESS_KEY = f"{data[1]}"

        s3 = boto3.client("s3", aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)

        file_path = fr"{data[2]}"
        bucket_name = f"{data[3]}"
        object_key = f"backupsql_{dt.datetime.now().strftime('%Y-%m-%d')}"

        s3.upload_file(file_path, bucket_name, object_key)

        response = s3.head_object(Bucket=bucket_name, Key=object_key)

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print("File uploaded successfully")
        else:
            print("File upload failed")

    def convertForm(self):
        self.ConvertForm = convertFormUI()
        self.ConvertForm.my_signal.connect(self.convert)

    def convert(self,data):
        self.fieldsLines = self.fields.toPlainText().split(" ")

        self.progressBar.setValue(10)

        self.dataList = data

        sql_connection = mysql.connector.connect(
            host=f'{data[2]}',
            user=f'{data[3]}',
            password=f'{data[1]}',
            database=f'{data[0]}'
        )

        self.progressBar.setValue(20)

        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client[f'{data[4]}']
        mongo_collection = mongo_db[f'{data[5]}']

        sql_cursor = sql_connection.cursor()
        if self.screen3DropDown.currentIndex() == 0:
            sql_cursor.execute(f'SELECT * FROM {data[6]}')
            sql_data = sql_cursor.fetchall()

            self.progressBar.setValue(45)

            j = 0
            for row in sql_data:
                doc = {}
                j += 5
                for i, myfield in enumerate(self.fieldsLines):
                    doc[myfield] = row[i]
                    self.progressBar.setValue(45 + j)

                mongo_collection.insert_one(doc)

                self.msgBox.setText(f"Data has been converted successfully")
                self.msgBox.exec()
                self.progressBar.setValue(0)
        elif self.screen3DropDown.currentIndex() == 1:
            try:
                mongo_documents = []
                for field in self.fieldsLines:
                    mongo_documents.extend(list(mongo_db[f'{data[5]}'].find({}, {field: 1})))

                document_list = [doc for doc in mongo_documents]

                data_frame = pd.DataFrame(document_list)

                mongo_client.close()

                cursor = sql_cursor

                table_name = 'client'

                df_filled = data_frame.fillna('')

                self.progressBar.setValue(45)

                for _, row in df_filled.iterrows():
                    values = [row[column] if not pd.isnull(row[column]) else '' for column in self.fieldsLines]
                    insert_query = f"INSERT IGNORE INTO {table_name} ({', '.join(self.fieldsLines)}) VALUES ({', '.join(['%s'] * len(self.fieldsLines))})"
                    cursor.execute(insert_query, values)

                sql_connection.commit()
                self.msgBox.exec()
                sql_cursor.close()
                sql_connection.close()

                self.progressBar.setValue(80)
                self.progressBar.setValue(100)
                self.msgBox.setText(f"Data has been converted successfully")
                self.msgBox.exec()

                self.progressBar.setValue(0)
            except Exception as e:
                self.msgBox.setText(f"{str(e)}")
                self.msgBox.exec()

        self.progressBar.setValue(100)

        self.progressBar.setValue(0)

    def saveConvert(self):
        try:
            if self.screen3DropDown.currentIndex() == 0:
                client = MongoClient('mongodb://localhost:27017/')

                db = client[f'{self.dataList[4]}']
                collection = db[f'{self.dataList[5]}']

                documents = collection.find()

                document_list = [doc for doc in documents]

                json_data = json.dumps(document_list, default=json_util.default, indent=4)

                filepath = "output.json"

                if(os.path.isfile(filepath)):
                    i = 1
                    filepath = f"output{i}.json"
                    while(os.path.isfile(filepath)):
                        i = i + 1
                        filepath = f"output{i}.json"

                with open(f'{filepath}', 'w') as file:
                    file.write(json_data)

                client.close()
            elif self.screen3DropDown.currentIndex() == 1:
                if self.convertSQLTable.rowCount() != 0:
                    rows = self.convertSQLTable.rowCount()
                    columns = self.convertSQLTable.columnCount()

                    data = []
                    for row in range(rows):
                        row_data = []
                        for column in range(columns):
                            item = self.convertSQLTable.item(row, column)
                            if item is not None:
                                row_data.append(item.text())
                            else:
                                row_data.append('')
                        data.append(row_data)
                    
                    df = pd.DataFrame(data)

                    options = QFileDialog.Options()
                    options |= QFileDialog.DontUseNativeDialog
                    options |= QFileDialog.AnyFile

                    file_path, _ = QFileDialog.getSaveFileName(None, "Save File", "", "Excel Files (*.xlsx)", options=options)

                    print(file_path)

                    try:
                        df.to_excel(f"{file_path}.xlsx", index=False)
                    except Exception as e:
                        self.msgBox.setText(f"Something went wrong: {e.message}")
                        self.msgBox.exec()
        except Exception as e:
            self.msgBox.setText(f"Please use convert first")
            self.msgBox.exec()

    def previewConvert(self):
        self.msgBox = QMessageBox()
        try:
            if self.screen3DropDown.currentIndex() == 0:
                self.PreviewBox.clear()
                client = MongoClient('mongodb://localhost:27017/')

                db = client[f'{self.dataList[4]}']
                collection = db[f'{self.dataList[5]}']

                documents = collection.find()

                document_list = [doc for doc in documents]

                json_data = json.dumps(document_list, default=json_util.default, indent=4)

                self.PreviewBox.setPlainText(json_data)

                client.close()
            elif self.screen3DropDown.currentIndex() == 1:
                self.convertSQLTable.clearContents()

                mydatabase = mysql.connector.connect(
                        host=f"{self.dataList[2]}",
                        user=f"{self.dataList[3]}",
                        password=f"{self.dataList[1]}",
                        database=f"{self.dataList[0]}"
                    )

                df = pd.read_sql_query(fr'SELECT * FROM {self.dataList[6]};', mydatabase)

                self.convertSQLTable.setColumnCount(len(df.columns))
                self.convertSQLTable.setRowCount(len(df))

                headers = df.columns.tolist()
                self.convertSQLTable.setHorizontalHeaderLabels(headers)

                for i, row in enumerate(df.values):
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.convertSQLTable.setItem(i, j, item)
    
        except Exception as e:
            self.msgBox.setText(f"Please use convert first")
            self.msgBox.exec()

    def changeWidgetsOnThirdScreen(self):
        if self.screen3DropDown.currentIndex() == 0:
            self.FromToText.setText("From SQL to")
            self.PreviewBox.setVisible(True)
            self.convertSQLTable.setVisible(False)
        elif self.screen3DropDown.currentIndex() == 1:
            self.FromToText.setText("From Mongo to")
            self.PreviewBox.setVisible(False)
            self.convertSQLTable.setVisible(True)

if __name__ == '__main__':
    # initialize the app
    app = QApplication(sys.argv)
    UiWindow = UI()
    app.exec_()
