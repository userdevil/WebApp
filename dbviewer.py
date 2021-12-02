import sqlite3
connection = sqlite3.connect("database.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM urls")
print("fetching all records one by one:")
result = cursor.fetchone()
while result is not None:
      print(result)
      result = cursor.fetchone()
