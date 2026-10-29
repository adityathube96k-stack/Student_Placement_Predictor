
import sqlite3

db_path = "instance/placement.db"

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Display all tables
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")

tables = cursor.fetchall()

print("\n=== DATABASE TABLES ===")
for (table_name,) in tables:
    print(f"\nTable: {table_name}")

    cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 10')
    rows = cursor.fetchall()

    columns = [description[0] for description in cursor.description]
    print("Columns:", columns)

    for row in rows:
        print(row)

connection.close()
