
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connection_timeout=5
    )

    print("SUCCESS! MySQL connection established.")
    print("Database:", connection.database)

    connection.close()

except mysql.connector.Error as error:
    print("CONNECTION FAILED!")
    print("Error:", error)
