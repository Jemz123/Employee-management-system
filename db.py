import mysql.connector
import os

def get_db_connection():
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DB")
    port = os.getenv("MYSQL_PORT")
    ssl_ca = os.getenv("MYSQL_SSL_CA")

    missing = [v for v in [host, user, password, database, port, ssl_ca] if not v]
    if missing:
        raise ValueError(f"Missing environment variables: {missing}")

    try:
        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port),
            ssl_ca=ssl_ca
        )
    except mysql.connector.Error as e:
        print("DB connection failed:", e)
        raise
