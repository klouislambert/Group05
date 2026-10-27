import pandas as pd
import re
from datetime import datetime

room = pd.read_csv("09_Source_Data/room_bookings.csv", dtype=str, keep_default_na=False)

# --- Look at the problems first ---
print("Rows:", len(room))
print("RoomNumber spellings:", room["RoomNumber"].nunique())
print("Empty StudentID (walk-ins):", (room["StudentID"] == "").sum())

# --- Rule 1: room numbers become R101 (keep only the digits) ---
def clean_room(x):
    digits = re.sub(r"\D", "", x)
    return "R" + digits

room["room_clean"] = room["RoomNumber"].apply(clean_room)
print("Rooms after cleaning:", room["room_clean"].nunique())

# --- Rule 2: time slots become Morning / Afternoon / Evening ---
SLOT_MAP = {
    "morning": "Morning", "am": "Morning", "8am-10am": "Morning", "10am-12pm": "Morning",
    "afternoon": "Afternoon", "pm": "Afternoon", "12pm-2pm": "Afternoon", "2pm-4pm": "Afternoon",
    "evening": "Evening", "5pm-7pm": "Evening", "7pm-9pm": "Evening",
}
room["slot_clean"] = room["TimeSlot"].str.strip().str.lower().map(SLOT_MAP).fillna("Unknown")
print("\nTime slots after cleaning:")
print(room["slot_clean"].value_counts())

# --- Rule 3: dates become YYYY-MM-DD ---
def clean_date(x):
    x = x.strip()
    for fmt in ("%Y-%m-%d", "%d-%b-%Y"):
        try:
            return datetime.strptime(x, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None

room["date_clean"] = room["BookingDate"].apply(clean_date)
print("\nBookingDate that could not be converted:", room["date_clean"].isna().sum())

# --- Rule 4: remove duplicates ---
rows_before = len(room)
room = room.drop_duplicates()
room = room.drop_duplicates(subset=["BookingID"])
print("\nRows before:", rows_before, "| after removing duplicates:", len(room))

# --- Rule 5: walk-ins (no StudentID) become UNKNOWN, rows are kept ---
walk_ins = (room["StudentID"].str.strip() == "").sum()
room["StudentID_clean"] = room["StudentID"].str.strip().replace("", "UNKNOWN")
print("Walk-in bookings marked UNKNOWN:", walk_ins)

# --- Rule 6: validate booking length (0.5 to 8 hours) ---
room["hours_clean"] = pd.to_numeric(room["DurationHours"], errors="coerce")
invalid = ~room["hours_clean"].between(0.5, 8)
print("Invalid DurationHours:", invalid.sum())
room = room[~invalid]

print("\nFinal rows:", len(room))