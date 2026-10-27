import pandas as pd
from datetime import datetime

sheets = pd.read_excel("09_Source_Data/digital_usage.xlsx", sheet_name=None, dtype=str, keep_default_na=False)
digital = pd.concat([df.assign(sheet=name) for name, df in sheets.items()], ignore_index=True)

# --- Look at the problems first ---
print("Rows:", len(digital))
print("ResourceType spellings:", digital["ResourceType"].nunique())
print("Faculty spellings:", digital["Faculty"].nunique())
print("DownloadCount with commas:", digital["DownloadCount"].str.contains(",").sum())
print("Missing Duration_Minutes:", (digital["Duration_Minutes"].str.strip() == "").sum())

# --- Rule 1: dates become YYYY-MM-DD (each sheet has its own format) ---
DATE_FORMATS = {"Sheet_MDY": "%m/%d/%Y", "Sheet_YDM": "%Y-%d-%m", "Sheet_Mon": "%b %d, %Y"}

def clean_date(row):
    try:
        return datetime.strptime(row["Date"].strip(), DATE_FORMATS[row["sheet"]]).strftime("%Y-%m-%d")
    except ValueError:
        return None

digital["date_clean"] = digital.apply(clean_date, axis=1)
print("\nDates that could not be converted:", digital["date_clean"].isna().sum())

# --- Rule 2: faculty names become standard department names ---
DEPT_MAP = {
    "cs": "Computer Science", "computer science": "Computer Science", "compsci": "Computer Science",
    "eng": "Engineering", "engineering": "Engineering", "engr": "Engineering",
    "bus": "Business", "business": "Business",
    "med": "Medicine", "medicine": "Medicine",
    "edu": "Education", "education": "Education", "educ": "Education",
    "law": "Law",
    "art": "Arts", "arts": "Arts",
}
digital["department_clean"] = digital["Faculty"].str.strip().str.lower().map(DEPT_MAP).fillna("Unknown")
print("\nDepartments after cleaning:")
print(digital["department_clean"].value_counts())

# --- Rule 3: resource types (E-book, e-Book, E-Book all become E-book) ---
RES_MAP = {"ebook": "E-book", "journal": "Journal", "article": "Article"}
key = digital["ResourceType"].str.strip().str.lower().str.replace("-", "", regex=False)
digital["resource_clean"] = key.map(RES_MAP).fillna("Unknown")
print("\nResource types after cleaning:")
print(digital["resource_clean"].value_counts())

# --- Rule 4: user types ---
USER_MAP = {"student": "Student", "staff": "Staff", "faculty": "Faculty", "grad student": "Grad Student"}
digital["user_clean"] = digital["UserType"].str.strip().str.lower().map(USER_MAP).fillna("Unknown")

# --- Rule 5: download counts (remove commas, convert to number) ---
digital["downloads_clean"] = pd.to_numeric(digital["DownloadCount"].str.replace(",", "", regex=False), errors="coerce")
print("\nInvalid DownloadCount:", (digital["downloads_clean"].isna() | (digital["downloads_clean"] < 0)).sum())

# --- Rule 6: missing duration stays empty (we do not invent numbers) ---
digital["duration_clean"] = pd.to_numeric(digital["Duration_Minutes"], errors="coerce")
print("Missing duration kept as empty:", digital["duration_clean"].isna().sum())

print("\nFinal rows:", len(digital))