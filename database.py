
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "electronics.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            password TEXT NOT NULL
        )
    """)

    user = conn.execute(
        "SELECT id FROM users WHERE id = 1"
    ).fetchone()

    if user is None:
        conn.execute("""
            INSERT INTO users
            (id, name, email, phone, address, password)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            1,
            "Dhakshana",
            "dhakshana@gmail.com",
            "9876543210",
            "Coimbatore, Tamil Nadu",
            generate_password_hash("demo123")
        ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_table()
    print("Database created successfully!")
