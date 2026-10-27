import pandas as pd

book = pd.read_csv("09_Source_Data/book_transactions.csv", dtype=str, keep_default_na=False)

DEPT_MAP = {
    "cs": "Computer Science",
    "computer science": "Computer Science",
    "compsci": "Computer Science",
    "eng": "Engineering",
    "engineering": "Engineering",
    "engr": "Engineering",
    "bus": "Business",
    "business": "Business",
    "med": "Medicine",
    "medicine": "Medicine",
    "edu": "Education",
    "education": "Education",
    "educ": "Education",
    "law": "Law",
    "art": "Arts",
    "arts": "Arts",
}

def clean_dept(x):
    key = x.strip().lower()
    return DEPT_MAP.get(key, "Unknown")

book["Department_clean"] = book["Department"].apply(clean_dept)
print(book["Department_clean"].value_counts())

# --- Rule 2: fill missing departments from the student master ---
master = pd.read_csv("09_Source_Data/student_master.csv", dtype=str)
student_dept = dict(zip(master["StudentID"], master["Department"]))

missing = book["Department_clean"] == "Unknown"
book.loc[missing, "Department_clean"] = book.loc[missing, "StudentID"].map(student_dept)
book["Department_clean"] = book["Department_clean"].fillna("Unknown")

print("\nAfter filling from student master:")
print(book["Department_clean"].value_counts())

# --- Rule 3: unify dates to ISO format YYYY-MM-DD ---
from datetime import datetime

def clean_date(x):
    x = x.strip()
    if x == "":
        return None                      # not returned yet: keep empty
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(x, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass                         # wrong format, try the next one
    return None                          # nothing matched

book["CheckoutDate_clean"] = book["CheckoutDate"].apply(clean_date)

print("\nCheckoutDate examples (before and after):")
print(book[book["CheckoutDate"].str.contains("/")][["CheckoutDate", "CheckoutDate_clean"]].head())
print("CheckoutDate that could not be converted:", book["CheckoutDate_clean"].isna().sum())
book["ReturnDate_clean"] = book["ReturnDate"].apply(clean_date)
print("Empty ReturnDate_clean:", book["ReturnDate_clean"].isna().sum())
# --- Rule 4: remove duplicate records ---
rows_before = len(book)
book = book.drop_duplicates()                              # exact duplicates
book = book.drop_duplicates(subset=["TransactionID"])      # same transaction ID twice
print("\nRows before:", rows_before, "| Rows after removing duplicates:", len(book))

# --- Rule 5: validate dates (return date must not be before checkout date) ---
bad = book["ReturnDate_clean"].notna() & (book["ReturnDate_clean"] < book["CheckoutDate_clean"])
print("Return date before checkout date:", bad.sum())
book.loc[bad, "ReturnDate_clean"] = None                   # set to empty and keep the row

# --- Rule 6: calculate loan duration in days ---
checkout = pd.to_datetime(book["CheckoutDate_clean"])
returned = pd.to_datetime(book["ReturnDate_clean"])
book["loan_days"] = (returned - checkout).dt.days          # empty when not returned
print("Average loan days:", round(book["loan_days"].mean(), 1))
print("Rows with no loan_days (not returned):", book["loan_days"].isna().sum())