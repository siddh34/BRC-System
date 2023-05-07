# import os, datetime as dt
# import mysql.connector

# sql_files = []
# for root, dirs, files in os.walk("./Storage"):
#     for file in files:  
#         if file.endswith('.sql'):
#             file_path = os.path.join(root, file)
#             size = os.path.getsize(file_path)
#             modified_timestamp = os.path.getmtime(file_path)
#             modified_datetime = dt.datetime.fromtimestamp(modified_timestamp)
#             modified_str = modified_datetime.strftime('%Y-%m-%d %H:%M:%S')
#             sql_files.append({
#                 'name': file,
#                 'size': size,
#                 'modified': modified_str
#             })

# print(sql_files[0]['name'])

# Creating connection object
# mydb = mysql.connector.connect(
#     host = "localhost",
#     user = "root",
#     password = "sid34",
#     database = "siddata"
# )

# # Printing the connection object
# print(mydb)

# cursor = mydb.cursor(buffered=True)

# cursor.execute("SHOW TABLES;")

# items = cursor.fetchall()

# print(items)

# cursor.close()

import subprocess, datetime as dt

# Run the dir command and print the output to the console

backupName = f"sqlBackup_{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.sql"

result = subprocess.run(['mysqldump', '-u', 'root', '-psid34', 'siddata', '>', './Tests/mydatabase_backup.sql'], capture_output=True, text=True, shell=True)

print(result.stdout)
print(result.stderr)
