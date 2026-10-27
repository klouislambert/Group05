import sqlite3, sys

db_file = "library_dw.db"
sql_file = sys.argv[1]

con = sqlite3.connect(db_file)
with open(sql_file, "r") as f:
    con.executescript(f.read())
con.commit()

tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables in database:", [t[0] for t in tables])