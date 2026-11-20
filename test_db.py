from database import get_db_connection

try:
    connection = get_db_connection()

    if connection.is_connected():
        print("Database Connected Successfully!")

        cursor = connection.cursor()

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print("\nTables in electromart_db:")

        for table in tables:
            print(table[0])

        cursor.close()
        connection.close()

except Exception as e:
    print("Database Connection Failed:", e)