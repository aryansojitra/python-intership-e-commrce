import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("Checking myapp_register table columns:")
cursor.execute('PRAGMA table_info(myapp_register)')
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
