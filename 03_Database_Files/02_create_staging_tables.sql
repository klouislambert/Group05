-- Staging area: raw data exactly as received (all TEXT, nothing cleaned)
CREATE TABLE IF NOT EXISTS stg_book_transactions (
    TransactionID TEXT, StudentID TEXT, BookISBN TEXT, CheckoutDate TEXT,
    ReturnDate TEXT, Department TEXT, BookCategory TEXT,
    source_file TEXT, loaded_at TEXT
);

CREATE TABLE IF NOT EXISTS stg_digital_usage (
    Date TEXT, UserType TEXT, ResourceType TEXT, Faculty TEXT,
    DownloadCount TEXT, Duration_Minutes TEXT, sheet_name TEXT,
    source_file TEXT, loaded_at TEXT
);

CREATE TABLE IF NOT EXISTS stg_room_bookings (
    BookingID TEXT, RoomNumber TEXT, BookingDate TEXT, TimeSlot TEXT,
    StudentID TEXT, DurationHours TEXT, Purpose TEXT,
    source_file TEXT, loaded_at TEXT
);

CREATE TABLE IF NOT EXISTS stg_student_master (
    StudentID TEXT, Department TEXT, StudentLevel TEXT,
    source_file TEXT, loaded_at TEXT
);