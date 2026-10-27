import sqlite3
print("SQLite version:", sqlite3.sqlite_version)
con = sqlite3.connect("library_dw.db")
print(con.execute("SELECT 'it works'").fetchone())