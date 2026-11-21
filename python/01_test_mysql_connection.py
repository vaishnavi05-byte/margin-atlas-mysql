import getpass
import mysql.connector

password = getpass.getpass("Enter your MySQL password: ")

connection = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="margin_atlas_app",
    password=password,
    database="margin_atlas",
    use_pure=True,
    connection_timeout=10,
)

cursor = connection.cursor()

cursor.execute("SELECT DATABASE(), VERSION();")
database_name, server_version = cursor.fetchone()

print("Connection successful!")
print("Database:", database_name)
print("MySQL version:", server_version)

cursor.close()
connection.close()