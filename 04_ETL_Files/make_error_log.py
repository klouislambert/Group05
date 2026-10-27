import pandas as pd
import datetime as dt

book = pd.read_csv("09_Source_Data/book_transactions.csv", dtype=str, keep_default_na=False)
room = pd.read_csv("09_Source_Data/room_bookings.csv", dtype=str, keep_default_na=False)
dig = pd.concat(pd.read_excel("09_Source_Data/digital_usage.xlsx", sheet_name=None,
                              dtype=str, keep_default_na=False).values(), ignore_index=True)

now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
LIMIT = 5      # sample lines written per rule (the totals cover all records)

checks = [
    # (rule, source, rows with the problem, key column, detail text, action taken)
    ("B5_DUPLICATE_ROW", "book", book[book.duplicated()], "TransactionID",
     lambda r: "identical row repeated", "dropped, first copy kept"),
    ("B2_MISSING_DEPARTMENT", "book", book[book["Department"] == ""], "TransactionID",
     lambda r: f"student {r['StudentID']}", "filled from student master"),
    ("B3_DATE_FORMAT", "book", book[~book["CheckoutDate"].str.match(r"^\d{4}-\d{2}-\d{2}$")], "TransactionID",
     lambda r: f"CheckoutDate {r['CheckoutDate']}", "converted to YYYY-MM-DD"),
    ("B4_NOT_RETURNED", "book", book[book["ReturnDate"] == ""], "TransactionID",
     lambda r: "ReturnDate empty", "kept as NULL, flagged not returned"),
    ("D4_COMMA_IN_COUNT", "digital", dig[dig["DownloadCount"].str.contains(",")], "Date",
     lambda r: f"DownloadCount {r['DownloadCount']}", "comma removed, converted to integer"),
    ("D5_MISSING_DURATION", "digital", dig[dig["Duration_Minutes"] == ""], "Date",
     lambda r: "Duration_Minutes empty", "kept as NULL, no invented value"),
    ("R4_DUPLICATE_ROW", "room", room[room.duplicated()], "BookingID",
     lambda r: "identical row repeated", "dropped, first copy kept"),
    ("R5_WALK_IN", "room", room[room["StudentID"] == ""], "BookingID",
     lambda r: "no StudentID", "kept, linked to Unknown student"),
]

lines = [f"ETL ERROR LOG (sample) - generated {now}",
         "timestamp | rule | source | record | detail | action", "-" * 90]
totals = []
for rule, source, df, keycol, detail, action in checks:
    totals.append((rule, len(df)))
    for _, r in df.head(LIMIT).iterrows():
        lines.append(f"{now} | {rule} | {source} | {r[keycol]} | {detail(r)} | {action}")
lines += ["", "TOTALS PER RULE (all records, not only the samples above)", "-" * 90]
lines += [f"{rule:25} {n:>6}" for rule, n in totals]

open("04_ETL_Files/error_log_sample.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))