import random, datetime as dt, pathlib
import pandas as pd
random.seed(42)
OUT = pathlib.Path(__file__).resolve().parent

DEPTS = {
 "Computer Science": ["CS", "Computer Science", "CompSci"],
 "Engineering": ["ENG", "Engineering", "Engr"],
 "Business": ["BUS", "Business", "Bus"],
 "Medicine": ["MED", "Medicine", "Med"],
 "Education": ["EDU", "Education", "Educ"],
 "Law": ["LAW", "Law", "Law"],
 "Arts": ["ART", "Arts", "Art"],
}
dept_names = list(DEPTS)
dept_w = [25, 22, 18, 12, 10, 7, 6]

students = []
for i in range(1, 301):
    yr = random.choice([2021, 2022, 2023, 2024])
    students.append({"StudentID": f"STU-{yr}-{i:03d}",
                     "Department": random.choices(dept_names, dept_w)[0],
                     "StudentLevel": random.choices(["Undergraduate", "Graduate"], [75, 25])[0]})
pd.DataFrame(students).to_csv(OUT / "student_master.csv", index=False)

def rand_date(a=dt.date(2024, 1, 1), b=dt.date(2025, 6, 30)):
    return a + dt.timedelta(days=random.randint(0, (b - a).days))

# ---- Source 1: book_transactions.csv ----
books = [(f"978-{random.randint(10**9, 10**10 - 1)}", random.choices(["Fiction", "Reference", "Textbook"], [30, 15, 55])[0]) for _ in range(120)]
book_w = [1 / (i + 1) ** 0.8 for i in range(len(books))]
rows = []
for n in range(3000):
    s = random.choice(students)
    isbn, cat = random.choices(books, book_w)[0]
    co = rand_date()
    ret = None if random.random() < 0.15 else co + dt.timedelta(days=random.randint(3, 45))
    dept = random.choice(DEPTS[s["Department"]])
    if random.random() < 0.03:
        dept = ""
    dmy = random.random() < 0.30
    f = lambda d: "" if d is None else (d.strftime("%d/%m/%Y") if dmy else d.isoformat())
    rows.append([1001 + n, s["StudentID"], isbn, f(co), f(ret), dept, cat])
bt = pd.DataFrame(rows, columns=["TransactionID", "StudentID", "BookISBN", "CheckoutDate", "ReturnDate", "Department", "BookCategory"])
bt = pd.concat([bt, bt.sample(25, random_state=1)], ignore_index=True)   # exact duplicates
bt.sample(frac=1, random_state=3).to_csv(OUT / "book_transactions.csv", index=False)

# ---- Source 2: digital_usage.xlsx (3 sheets, 3 date formats) ----
def digital_rows(n, fmt):
    out = []
    for _ in range(n):
        d = rand_date()
        ds = {"mdy": d.strftime("%m/%d/%Y"), "ydm": f"{d.year}-{d.day:02d}-{d.month:02d}", "mon": d.strftime("%b %d, %Y")}[fmt]
        fac = random.choices(dept_names, dept_w)[0]
        cnt = random.choices([1, 3, 5, 12, 23, 150, 1200], [30, 25, 20, 12, 8, 4, 1])[0]
        cnt_s = f"{cnt:,}" if cnt >= 1000 else str(cnt)
        dur = "" if random.random() < 0.25 else str(random.choice([5, 15, 30, 45, 60, 90, 120]))
        out.append([ds, random.choices(["Student", "Staff", "Faculty", "Grad Student"], [55, 8, 12, 25])[0],
                    random.choices(["E-book", "e-Book", "E-Book", "Journal", "journal", "Article"], [25, 10, 5, 25, 5, 30])[0],
                    random.choice(DEPTS[fac]), cnt_s, dur])
    return pd.DataFrame(out, columns=["Date", "UserType", "ResourceType", "Faculty", "DownloadCount", "Duration_Minutes"])
with pd.ExcelWriter(OUT / "digital_usage.xlsx") as w:
    digital_rows(700, "mdy").to_excel(w, sheet_name="Sheet_MDY", index=False)
    digital_rows(700, "ydm").to_excel(w, sheet_name="Sheet_YDM", index=False)
    digital_rows(700, "mon").to_excel(w, sheet_name="Sheet_Mon", index=False)

# ---- Source 3: room_bookings.csv ----
slots = {"Morning": ["Morning", "8AM-10AM", "AM", "10AM-12PM"], "Afternoon": ["Afternoon", "12PM-2PM", "2PM-4PM", "PM"],
         "Evening": ["Evening", "5PM-7PM", "7PM-9PM"]}
rb = []
for n in range(1500):
    d = rand_date()
    r = random.choices(range(101, 111), [20, 16, 14, 12, 10, 8, 7, 6, 4, 3])[0]
    sl = random.choice(random.choices(list(slots.values()), [40, 40, 20])[0])
    sid = "" if random.random() < 0.08 else random.choice(students)["StudentID"]
    ds = d.isoformat() if random.random() < 0.6 else d.strftime("%d-%b-%Y")
    rb.append([5001 + n, random.choice([f"R{r}", f"R-{r}", f"Room{r}"]), ds, sl, sid,
               random.choice(["1.0", "2.0", "2.0", "3.0", "3.5"]),
               random.choices(["Study", "Group Project", "Meeting"], [45, 40, 15])[0]])
rb = pd.DataFrame(rb, columns=["BookingID", "RoomNumber", "BookingDate", "TimeSlot", "StudentID", "DurationHours", "Purpose"])
rb = pd.concat([rb, rb.sample(40, random_state=4)], ignore_index=True)   # exact duplicates
rb.sample(frac=1, random_state=6).to_csv(OUT / "room_bookings.csv", index=False)
print("Done: 4 files created in 09_Source_Data")