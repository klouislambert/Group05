import sqlite3
import datetime as dt
import pandas as pd

con = sqlite3.connect("library_dw.db")
ts = dt.datetime.now().isoformat(timespec="seconds")

book = pd.read_csv("09_Source_Data/book_transactions.csv", dtype=str, keep_default_na=False)
room = pd.read_csv("09_Source_Data/room_bookings.csv", dtype=str, keep_default_na=False)
master = pd.read_csv("09_Source_Data/student_master.csv", dtype=str, keep_default_na=False)
sheets = pd.read_excel("09_Source_Data/digital_usage.xlsx", sheet_name=None, dtype=str, keep_default_na=False)
digital = pd.concat([df.assign(sheet_name=name) for name, df in sheets.items()], ignore_index=True)

loads = [
    ("stg_book_transactions", book, "book_transactions.csv"),
    ("stg_digital_usage", digital, "digital_usage.xlsx"),
    ("stg_room_bookings", room, "room_bookings.csv"),
    ("stg_student_master", master, "student_master.csv"),
]

print(f"{'staging table':24}{'source rows':>12}{'staged rows':>12}  check")
for table, df, source in loads:
    con.execute(f"DELETE FROM {table}")            # staging is replaced on every run
    df.assign(source_file=source, loaded_at=ts).to_sql(table, con, if_exists="append", index=False)
    staged = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table:24}{len(df):>12}{staged:>12}  {'OK' if staged == len(df) else 'MISMATCH'}")
con.commit()