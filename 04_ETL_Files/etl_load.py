import sqlite3
import datetime as dt
import pandas as pd

# Importing runs your three cleaning scripts and gives us their clean tables
import clean_books, clean_rooms, clean_digital
book = clean_books.book
room = clean_rooms.room
digital = clean_digital.digital
master = pd.read_csv("09_Source_Data/student_master.csv", dtype=str)

con = sqlite3.connect("library_dw.db")
cur = con.cursor()

# INSERT OR IGNORE = safe to run again, existing rows are skipped

# --- dim_department (key 0 = Unknown) ---
depts = ["Unknown", "Computer Science", "Engineering", "Business", "Medicine", "Education", "Law", "Arts"]
for key, name in enumerate(depts):
    cur.execute("INSERT OR IGNORE INTO dim_department(department_key, department_name) VALUES (?,?)", (key, name))

# --- dim_user_type ---
for key, name in enumerate(["Unknown", "Student", "Grad Student", "Staff", "Faculty"]):
    cur.execute("INSERT OR IGNORE INTO dim_user_type(user_type_key, user_type) VALUES (?,?)", (key, name))

# --- dim_room: the 10 clean room codes ---
for code in sorted(room["room_clean"].unique()):
    cur.execute("INSERT OR IGNORE INTO dim_room(room_code) VALUES (?)", (code,))

# --- dim_timeslot ---
for name, start, end in [("Morning", 8, 12), ("Afternoon", 12, 17), ("Evening", 17, 21)]:
    cur.execute("INSERT OR IGNORE INTO dim_timeslot(slot_name, start_hour, end_hour) VALUES (?,?,?)", (name, start, end))

# --- dim_date: every day from 2023 to 2026 ---
d = dt.date(2023, 1, 1)
while d <= dt.date(2026, 12, 31):
    cur.execute("INSERT OR IGNORE INTO dim_date VALUES (?,?,?,?,?,?,?,?,?,?)",
                (int(d.strftime("%Y%m%d")), d.isoformat(), d.strftime("%A"), d.isocalendar()[1],
                 d.month, d.strftime("%B"), d.strftime("%Y-%m"), (d.month - 1) // 3 + 1,
                 d.year, int(d.isoweekday() >= 6)))
    d += dt.timedelta(days=1)

# --- dim_resource: 3 digital types + every book (ISBN + category) ---
for t in ["E-book", "Journal", "Article"]:
    cur.execute("INSERT OR IGNORE INTO dim_resource(resource_type) VALUES (?)", (t,))
for isbn, cat in book[["BookISBN", "BookCategory"]].drop_duplicates().itertuples(index=False):
    cur.execute("INSERT OR IGNORE INTO dim_resource(resource_type, book_isbn, book_category) VALUES ('Book',?,?)", (isbn, cat))

# --- dim_student (key 0 = Unknown, used for walk-ins) ---
dept_key = dict(cur.execute("SELECT department_name, department_key FROM dim_department"))
cur.execute("INSERT OR IGNORE INTO dim_student(student_key, student_id, student_level, department_key) VALUES (0,'UNKNOWN','Unknown',0)")
for r in master.itertuples():
    cur.execute("INSERT OR IGNORE INTO dim_student(student_id, student_level, department_key) VALUES (?,?,?)",
                (r.StudentID, r.StudentLevel, dept_key[r.Department]))

con.commit()

print("\n===== Dimension tables loaded =====")
for t in ["dim_department", "dim_user_type", "dim_room", "dim_timeslot", "dim_date", "dim_resource", "dim_student"]:
    print(t, cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
    
# ================= FACT TABLES =================
# Full load: empty the fact tables first, then load everything again
for t in ["fact_book_loan", "fact_digital_usage", "fact_room_booking"]:
    cur.execute(f"DELETE FROM {t}")

def dkey(s):                          # "2024-03-15" -> 20240315
    return int(s.replace("-", ""))

def none_if_nan(x):
    return None if pd.isna(x) else x

# Lookups: business value -> surrogate key
stud_key = dict(cur.execute("SELECT student_id, student_key FROM dim_student"))
dept_key = dict(cur.execute("SELECT department_name, department_key FROM dim_department"))
user_key = dict(cur.execute("SELECT user_type, user_type_key FROM dim_user_type"))
room_key = dict(cur.execute("SELECT room_code, room_key FROM dim_room"))
slot_key = dict(cur.execute("SELECT slot_name, timeslot_key FROM dim_timeslot"))
book_res = {(i, c): k for k, i, c in cur.execute(
    "SELECT resource_key, book_isbn, book_category FROM dim_resource WHERE resource_type='Book'")}
dig_res = dict(cur.execute("SELECT resource_type, resource_key FROM dim_resource WHERE resource_type != 'Book'"))
student_dept = dict(zip(master["StudentID"], master["Department"]))

# --- fact_book_loan ---
loans = []
for r in book.itertuples():
    ret = none_if_nan(r.ReturnDate_clean)
    loans.append((int(r.TransactionID), dkey(r.CheckoutDate_clean), dkey(ret) if ret else None,
                  stud_key.get(r.StudentID, 0), dept_key[r.Department_clean],
                  book_res[(r.BookISBN, r.BookCategory)],
                  None if pd.isna(r.loan_days) else int(r.loan_days), 1 if ret else 0))
cur.executemany("""INSERT INTO fact_book_loan(transaction_id, checkout_date_key, return_date_key,
                   student_key, department_key, resource_key, loan_days, is_returned)
                   VALUES (?,?,?,?,?,?,?,?)""", loans)

# --- fact_room_booking ---
rooms = []
for r in room.itertuples():
    sid = r.StudentID_clean
    rooms.append((int(r.BookingID), dkey(r.date_clean), room_key[r.room_clean], slot_key[r.slot_clean],
                  stud_key.get(sid, 0), dept_key[student_dept.get(sid, "Unknown")],
                  float(r.hours_clean), r.Purpose))
cur.executemany("""INSERT INTO fact_room_booking(booking_id, date_key, room_key, timeslot_key,
                   student_key, department_key, duration_hours, purpose)
                   VALUES (?,?,?,?,?,?,?,?)""", rooms)

# --- fact_digital_usage ---
digs = []
for r in digital.itertuples():
    digs.append((dkey(r.date_clean), dept_key[r.department_clean], user_key[r.user_clean],
                 dig_res[r.resource_clean], int(r.downloads_clean),
                 None if pd.isna(r.duration_clean) else int(r.duration_clean)))
cur.executemany("""INSERT INTO fact_digital_usage(date_key, department_key, user_type_key,
                   resource_key, download_count, duration_minutes)
                   VALUES (?,?,?,?,?,?)""", digs)

con.commit()

# --- Check the result ---
print("\n===== Fact tables loaded =====")
for t in ["fact_book_loan", "fact_digital_usage", "fact_room_booking"]:
    print(t, cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
print("Broken foreign keys:", len(cur.execute("PRAGMA foreign_key_check").fetchall()))

print("\nLoans per department (first real query on your warehouse):")
for row in cur.execute("""SELECT d.department_name, COUNT(*) FROM fact_book_loan f
                          JOIN dim_department d ON d.department_key = f.department_key
                          GROUP BY d.department_name ORDER BY 2 DESC"""):
    print(row)
con.close()