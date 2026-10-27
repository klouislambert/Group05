CREATE TABLE IF NOT EXISTS dim_department (
    department_key  INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_room (
    room_key  INTEGER PRIMARY KEY,
    room_code TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_timeslot (
    timeslot_key INTEGER PRIMARY KEY,
    slot_name    TEXT NOT NULL UNIQUE,
    start_hour   INTEGER,
    end_hour     INTEGER
);
CREATE TABLE IF NOT EXISTS dim_date (
    date_key     INTEGER PRIMARY KEY,   -- format YYYYMMDD, e.g. 20240315
    full_date    TEXT NOT NULL UNIQUE,  -- ISO format 2024-03-15
    day_name     TEXT,
    week_of_year INTEGER,
    month_num    INTEGER,
    month_name   TEXT,
    year_month   TEXT,                  -- e.g. 2024-03
    quarter      INTEGER,
    year         INTEGER,
    is_weekend   INTEGER
);

CREATE TABLE IF NOT EXISTS dim_resource (
    resource_key  INTEGER PRIMARY KEY,
    resource_type TEXT NOT NULL,        -- Book, E-book, Journal, Article
    book_isbn     TEXT NOT NULL DEFAULT 'N/A',
    book_category TEXT NOT NULL DEFAULT 'N/A',
    UNIQUE (resource_type, book_isbn, book_category)
);

CREATE TABLE IF NOT EXISTS dim_student (
    student_key    INTEGER PRIMARY KEY,
    student_id     TEXT NOT NULL UNIQUE,
    student_level  TEXT NOT NULL,       -- Undergraduate, Graduate, Unknown
    department_key INTEGER NOT NULL REFERENCES dim_department(department_key)
);
CREATE TABLE IF NOT EXISTS dim_user_type (
    user_type_key INTEGER PRIMARY KEY,
    user_type     TEXT NOT NULL UNIQUE
);