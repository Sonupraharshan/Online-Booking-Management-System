"""
Add genres column to existing book table.
Run this from the project root: python add_genres_column.py
"""
import pymysql

def add_genres_column():
    # Connect to database
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='bookstore_db'
    )
    
    try:
        with connection.cursor() as cursor:
            # Check if column exists
            cursor.execute("SHOW COLUMNS FROM book LIKE 'genres'")
            result = cursor.fetchone()
            
            if result:
                print("✅ 'genres' column already exists!")
            else:
                # Add the column
                cursor.execute("ALTER TABLE book ADD COLUMN genres VARCHAR(255)")
                connection.commit()
                print("✅ Added 'genres' column to book table!")
                
    finally:
        connection.close()

if __name__ == '__main__':
    add_genres_column()
