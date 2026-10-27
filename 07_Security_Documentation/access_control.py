import sqlite3, re
import datetime as dt

con = sqlite3.connect("library_dw.db")
con.execute("""CREATE TABLE IF NOT EXISTS sec_audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_time TEXT, db_user TEXT, role TEXT, query TEXT, outcome TEXT, detail TEXT)""")

# Who has which role
USERS = {"admin_user": "admin", "analyst_user": "analyst", "head_eng": "dept_head"}

# What each role may read (None = everything)
ALLOWED = {
    "admin": None,
    "analyst": {"fact_book_loan", "fact_digital_usage", "fact_room_booking", "dim_date",
                "dim_department", "dim_resource", "dim_room", "dim_timeslot",
                "dim_user_type", "vw_student_masked"},          # NOT dim_student (real IDs)
    "dept_head": {"vw_head_engineering_loans", "dim_date", "dim_resource"},
}

def log(user, role, sql, outcome, detail=""):
    con.execute("INSERT INTO sec_audit_log(event_time, db_user, role, query, outcome, detail) VALUES (?,?,?,?,?,?)",
                (dt.datetime.now().isoformat(timespec="seconds"), user, role, sql, outcome, detail))
    con.commit()

def run_query(user, sql):
    role = USERS.get(user)
    if role is None:
        log(user, "none", sql, "DENIED", "unknown user")
        return "DENIED: unknown user"
    if not sql.strip().lower().startswith("select") and role != "admin":
        log(user, role, sql, "DENIED", "role is read-only")
        return "DENIED: this role is read-only"
    allowed = ALLOWED[role]
    used = set(re.findall(r"(?:from|join)\s+([a-z_]+)", sql.lower()))
    if allowed is not None and not used <= allowed:
        blocked = sorted(used - allowed)
        log(user, role, sql, "DENIED", f"no access to {blocked}")
        return f"DENIED: no access to {blocked}"
    rows = con.execute(sql).fetchall()
    log(user, role, sql, "ALLOWED", f"{len(rows)} rows")
    return rows

# ---------- Demonstration ----------
TESTS = [
    ("admin_user",   "SELECT COUNT(*) FROM dim_student"),
    ("analyst_user", "SELECT * FROM dim_student"),
    ("analyst_user", "SELECT * FROM vw_student_masked LIMIT 3"),
    ("analyst_user", "DELETE FROM fact_book_loan"),
    ("head_eng",     "SELECT COUNT(*) FROM fact_book_loan"),
    ("head_eng",     "SELECT COUNT(*) FROM vw_head_engineering_loans"),
    ("stranger",     "SELECT COUNT(*) FROM fact_book_loan"),
]
for user, sql in TESTS:
    print(f"{user:13} | {sql[:50]:50} -> {str(run_query(user, sql))[:70]}")

print("\nAudit log summary:")
for outcome, n in con.execute("SELECT outcome, COUNT(*) FROM sec_audit_log GROUP BY outcome"):
    print(" ", outcome, n)