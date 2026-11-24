import sqlite3

DB_NAME = "College.db"

def getAllStudent_db():
    Connection = sqlite3.connect(DB_NAME)
    cursor = Connection.cursor()
    cursor.execute("SELECT * FROM Students")
    rows = cursor.fetchall()
    Connection.close()
    return rows


def search_student_by_id(student_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    # Pass the parameter as a tuple: (student_id,)
    cursor.execute("SELECT name, course FROM Students WHERE id=?", (student_id,))
    
    # Use fetchone() since ID is usually unique (or fetchall() if expecting multiple)
    row = cursor.fetchone() 
    
    connection.close()
    return row