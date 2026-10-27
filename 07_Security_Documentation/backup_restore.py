import sqlite3, os, time
import datetime as dt

os.makedirs("backups", exist_ok=True)
stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
backup_file = f"backups/library_dw_full_{stamp}.db"
restore_file = "backups/restore_test.db"
TABLES = ["dim_department", "dim_student", "dim_date", "dim_resource",
          "fact_book_loan", "fact_digital_usage", "fact_room_booking"]

# 1. FULL BACKUP (SQLite's online backup is safe even while the database is in use)
src = sqlite3.connect("library_dw.db")
dst = sqlite3.connect(backup_file)
src.backup(dst)
dst.close()
print("Backup written:", backup_file, f"({os.path.getsize(backup_file) // 1024} KB)")

# 2. RESTORE TEST into a separate file, and time it
if os.path.exists(restore_file):
    os.remove(restore_file)
t0 = time.time()
bk = sqlite3.connect(backup_file)
rs = sqlite3.connect(restore_file)
bk.backup(rs)
seconds = time.time() - t0

# 3. VERIFY: integrity check + row counts must match the live database
print("Integrity check of restored copy:", rs.execute("PRAGMA integrity_check").fetchone()[0])
print(f"\n{'table':22}{'live':>8}{'restored':>10}")
all_ok = True
for t in TABLES:
    a = src.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    b = rs.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    all_ok = all_ok and (a == b)
    print(f"{t:22}{a:>8}{b:>10}")
print("\nRestore result:", "SUCCESS, all counts match" if all_ok else "FAILED")
print(f"Restore time: {seconds:.2f} seconds")