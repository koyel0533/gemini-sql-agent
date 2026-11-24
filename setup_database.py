import sqlite3

DB_NAME = "College.db"

def create_database():
    Connection = sqlite3.connect(DB_NAME)
    cursor = Connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
           course TEXT NOT NULL,
           marks Real NOT NULL,
           city TEXT NOT NULL
        )
    ''')

    cursor.execute("delete from Students")

    #Insert sample data into the Students table
    sample_data = [
        ("John Doe", "Computer Science", 85.5, "New York"),
        ("Jane Smith", "Mathematics", 92.0, "Los Angeles"),
        ("Alice Johnson", "Physics", 78.0, "Chicago"),
        ("Bob Brown", "Chemistry", 88.5, "Houston"),
        ("Charlie Davis", "Biology", 95.0, "Phoenix")
    ]

    cursor.executemany("INSERT INTO Students (name, course, marks, city) VALUES (?, ?, ?, ?)", sample_data)

    Connection.commit()
    Connection.close()

    print("Database Created and sample data inserted successfully.")
    print("Table:Students")
    print("5 sample records inserted into the Students table.")

if __name__ == "__main__":
    create_database()