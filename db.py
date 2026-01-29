import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",             # replace with your MySQL username
        password="happy@JUL11",  # replace with your MySQL password
        database="company_crud"
    )
