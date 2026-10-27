import sqlite3
import pandas as pd

book = pd.read_csv("09_Source_Data/book_transactions.csv", dtype=str, keep_default_na=False)
room = pd.read_csv("09_Source_Data/room_bookings.csv", dtype=str, keep_default_na=False)
sheets = pd.read_excel("09_Source_Data/digital_usage.xlsx", sheet_name=None, dtype=str, keep_default_na=False)
dig = pd.concat(sheets.values(), ignore_index=True)

con = sqlite3.connect("library_dw.db")
q = lambda s: con.execute(s).fetchone()[0]

rows = [
 # (source, metric, before (raw files), after (warehouse))
 ("Book loans", "Rows", len(book), q("SELECT COUNT(*) FROM fact_book_loan")),
 ("Book loans", "Duplicate rows", int(book.duplicated().sum()),
     q("SELECT COUNT(*) - COUNT(DISTINCT transaction_id) FROM fact_book_loan")),
 ("Book loans", "Department spellings", book["Department"].replace("", pd.NA).nunique(),
     q("SELECT COUNT(*) FROM dim_department WHERE department_key > 0")),
 ("Book loans", "Empty department", int((book["Department"] == "").sum()),
     q("SELECT COUNT(*) FROM fact_book_loan WHERE department_key = 0")),
 ("Book loans", "Dates not in YYYY-MM-DD", int((~book["CheckoutDate"].str.match(r"^\d{4}-\d{2}-\d{2}$")).sum()), 0),
 ("Book loans", "Empty ReturnDate (kept, not returned yet)", int((book["ReturnDate"] == "").sum()),
     q("SELECT COUNT(*) FROM fact_book_loan WHERE is_returned = 0")),
 ("Digital downloads", "Rows", len(dig), q("SELECT COUNT(*) FROM fact_digital_usage")),
 ("Digital downloads", "Resource type spellings", dig["ResourceType"].nunique(),
     q("SELECT COUNT(*) FROM dim_resource WHERE resource_type != 'Book'")),
 ("Digital downloads", "Faculty spellings", dig["Faculty"].nunique(),
     q("SELECT COUNT(DISTINCT department_key) FROM fact_digital_usage")),
 ("Digital downloads", "DownloadCount with commas", int(dig["DownloadCount"].str.contains(",").sum()),
     q("SELECT COUNT(*) FROM fact_digital_usage WHERE typeof(download_count) != 'integer'")),
 ("Digital downloads", "Missing Duration_Minutes (kept as NULL)", int((dig["Duration_Minutes"] == "").sum()),
     q("SELECT COUNT(*) FROM fact_digital_usage WHERE duration_minutes IS NULL")),
 ("Room bookings", "Rows", len(room), q("SELECT COUNT(*) FROM fact_room_booking")),
 ("Room bookings", "Duplicate rows", int(room.duplicated().sum()),
     q("SELECT COUNT(*) - COUNT(DISTINCT booking_id) FROM fact_room_booking")),
 ("Room bookings", "Room number spellings", room["RoomNumber"].nunique(),
     q("SELECT COUNT(*) FROM dim_room")),
 ("Room bookings", "Time slot spellings", room["TimeSlot"].str.lower().nunique(),
     q("SELECT COUNT(*) FROM dim_timeslot")),
 ("Room bookings", "Walk-ins without StudentID (kept as Unknown)", int((room["StudentID"] == "").sum()),
     q("SELECT COUNT(*) FROM fact_room_booking WHERE student_key = 0")),
 ("Warehouse", "Broken foreign keys", "n/a", len(con.execute("PRAGMA foreign_key_check").fetchall())),
]

lines = ["# Data Quality Report", "",
         "Before = raw source files. After = loaded warehouse.", "",
         "| Source | Metric | Before | After |", "|---|---|---|---|"]
for s, m, b, a in rows:
    lines.append(f"| {s} | {m} | {b} | {a} |")
open("04_ETL_Files/data_quality_report.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))