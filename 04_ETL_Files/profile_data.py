import pandas as pd

book = pd.read_csv("09_Source_Data/book_transactions.csv", dtype=str, keep_default_na=False)

print("Rows:", len(book))
print("\nDepartment spellings:")
print(book["Department"].value_counts())

iso = book["CheckoutDate"].str.match(r"^\d{4}-\d{2}-\d{2}$").sum()
print("\nCheckoutDate in YYYY-MM-DD format:", iso)
print("CheckoutDate in another format:", len(book) - iso)

print("\nEmpty ReturnDate (not returned):", (book["ReturnDate"] == "").sum())
print("Empty Department:", (book["Department"] == "").sum())
print("Exact duplicate rows:", book.duplicated().sum())