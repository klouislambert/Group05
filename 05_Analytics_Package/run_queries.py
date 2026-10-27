import sqlite3, re
import pandas as pd

con = sqlite3.connect("library_dw.db")
text = open("05_Analytics_Package/business_queries.sql").read()

# Each query starts with a line like "-- Q1: title"
parts = re.split(r"^-- (Q\d+):(.*)$", text, flags=re.M)

with pd.ExcelWriter("05_Analytics_Package/query_results.xlsx") as writer:
    for i in range(1, len(parts), 3):
        name, title, sql = parts[i], parts[i + 1].strip(), parts[i + 2]
        df = pd.read_sql_query(sql.strip().rstrip(";"), con)
        print(f"\n{name}: {title}")
        print(df.to_string(index=False))
        df.to_excel(writer, sheet_name=name, index=False)
print("\nSaved: 05_Analytics_Package/query_results.xlsx")