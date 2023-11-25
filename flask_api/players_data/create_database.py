"""
Python script to create a sqlite database and insert a test row inside.
This database is used for the mercato pick rate.
"""
import sqlite3

con = sqlite3.connect("flask_api/players_data/players_database.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS players (id TEXT PRIMARY KEY, mercato_pr REAL)")
con.commit()
cur.execute("INSERT OR IGNORE INTO players VALUES ('mpg_test', 1.0)")
con.commit()
print("Database created successfully")
con.close()
