CREATE TABLE IF NOT EXISTS fact_book_loan (
    loan_key          INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id    INTEGER NOT NULL UNIQUE,
    checkout_date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    return_date_key   INTEGER REFERENCES dim_date(date_key),
    student_key       INTEGER NOT NULL REFERENCES dim_student(student_key),
    department_key    INTEGER NOT NULL REFERENCES dim_department(department_key),
    resource_key      INTEGER NOT NULL REFERENCES dim_resource(resource_key),
    loan_days         INTEGER,
    is_returned       INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_room_booking (
    booking_key    INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id     INTEGER NOT NULL UNIQUE,
    date_key       INTEGER NOT NULL REFERENCES dim_date(date_key),
    room_key       INTEGER NOT NULL REFERENCES dim_room(room_key),
    timeslot_key   INTEGER NOT NULL REFERENCES dim_timeslot(timeslot_key),
    student_key    INTEGER NOT NULL REFERENCES dim_student(student_key),
    department_key INTEGER NOT NULL REFERENCES dim_department(department_key),
    duration_hours REAL NOT NULL,
    purpose        TEXT
);

CREATE TABLE IF NOT EXISTS fact_digital_usage (
    usage_key        INTEGER PRIMARY KEY AUTOINCREMENT,
    date_key         INTEGER NOT NULL REFERENCES dim_date(date_key),
    department_key   INTEGER NOT NULL REFERENCES dim_department(department_key),
    user_type_key    INTEGER NOT NULL REFERENCES dim_user_type(user_type_key),
    resource_key     INTEGER NOT NULL REFERENCES dim_resource(resource_key),
    download_count   INTEGER NOT NULL,
    duration_minutes INTEGER
);