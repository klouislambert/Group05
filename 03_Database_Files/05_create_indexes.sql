-- Index every foreign key that queries join or filter on
CREATE INDEX IF NOT EXISTS ix_loan_checkout  ON fact_book_loan(checkout_date_key);
CREATE INDEX IF NOT EXISTS ix_loan_dept      ON fact_book_loan(department_key);
CREATE INDEX IF NOT EXISTS ix_loan_resource  ON fact_book_loan(resource_key);
CREATE INDEX IF NOT EXISTS ix_dig_date       ON fact_digital_usage(date_key);
CREATE INDEX IF NOT EXISTS ix_dig_dept       ON fact_digital_usage(department_key);
CREATE INDEX IF NOT EXISTS ix_room_date      ON fact_room_booking(date_key);
CREATE INDEX IF NOT EXISTS ix_room_room      ON fact_room_booking(room_key);
CREATE INDEX IF NOT EXISTS ix_room_slot      ON fact_room_booking(timeslot_key);
CREATE INDEX IF NOT EXISTS ix_date_ym        ON dim_date(year_month);