-- Q1: Rank departments by total library usage (loans + downloads + bookings)
SELECT dep.department_name,
       SUM(CASE WHEN u.service = 'Loans'     THEN u.n END) AS loans,
       SUM(CASE WHEN u.service = 'Downloads' THEN u.n END) AS downloads,
       SUM(CASE WHEN u.service = 'Bookings'  THEN u.n END) AS bookings,
       SUM(u.n) AS total_usage
FROM (SELECT department_key, 'Loans' AS service, 1 AS n FROM fact_book_loan
      UNION ALL
      SELECT department_key, 'Downloads', download_count FROM fact_digital_usage
      UNION ALL
      SELECT department_key, 'Bookings', 1 FROM fact_room_booking) u
JOIN dim_department dep ON dep.department_key = u.department_key
GROUP BY dep.department_name
ORDER BY total_usage DESC;

-- Q2: Peak times for study rooms (day of week and time block)
SELECT d.day_name, t.slot_name, COUNT(*) AS bookings
FROM fact_room_booking f
JOIN dim_date d     ON d.date_key = f.date_key
JOIN dim_timeslot t ON t.timeslot_key = f.timeslot_key
GROUP BY d.day_name, t.slot_name
ORDER BY bookings DESC
LIMIT 10;

-- Q3: Average loan duration by department and book category (returned books only)
SELECT dep.department_name, r.book_category,
       ROUND(AVG(f.loan_days), 1) AS avg_loan_days,
       COUNT(*) AS returned_loans
FROM fact_book_loan f
JOIN dim_department dep ON dep.department_key = f.department_key
JOIN dim_resource r     ON r.resource_key = f.resource_key
WHERE f.is_returned = 1
GROUP BY dep.department_name, r.book_category
ORDER BY dep.department_name, r.book_category;
-- Q4: Top 10 most borrowed books
SELECT r.book_isbn, r.book_category, COUNT(*) AS times_borrowed
FROM fact_book_loan f
JOIN dim_resource r ON r.resource_key = f.resource_key
GROUP BY r.book_isbn, r.book_category
ORDER BY times_borrowed DESC
LIMIT 10;
-- Q5: DRILL-DOWN level 1: loans per year
SELECT d.year, COUNT(*) AS loans
FROM fact_book_loan f JOIN dim_date d ON d.date_key = f.checkout_date_key
GROUP BY d.year;

-- Q6: DRILL-DOWN level 2: quarters of 2024
SELECT d.year, d.quarter, COUNT(*) AS loans
FROM fact_book_loan f JOIN dim_date d ON d.date_key = f.checkout_date_key
WHERE d.year = 2024
GROUP BY d.year, d.quarter ORDER BY d.quarter;

-- Q7: DRILL-DOWN level 3: months of Q1 2024
SELECT d.year_month, COUNT(*) AS loans
FROM fact_book_loan f JOIN dim_date d ON d.date_key = f.checkout_date_key
WHERE d.year = 2024 AND d.quarter = 1
GROUP BY d.year_month ORDER BY d.year_month;

-- Q8: DRILL-DOWN level 4: days of March 2024
SELECT d.full_date, d.day_name, COUNT(*) AS loans
FROM fact_book_loan f JOIN dim_date d ON d.date_key = f.checkout_date_key
WHERE d.year_month = '2024-03'
GROUP BY d.full_date, d.day_name ORDER BY d.full_date;

-- Q9: ROLL-UP: daily room bookings aggregated to weeks
SELECT d.year, d.week_of_year, COUNT(*) AS bookings, ROUND(SUM(f.duration_hours), 1) AS hours
FROM fact_room_booking f JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.week_of_year ORDER BY d.year, d.week_of_year
LIMIT 10;

-- Q10: ROLL-UP: weeks aggregated to months
SELECT d.year_month, COUNT(*) AS bookings, ROUND(SUM(f.duration_hours), 1) AS hours
FROM fact_room_booking f JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year_month ORDER BY d.year_month;

-- Q11: SLICE: room bookings for one period only (Q1 2024), by department
SELECT dep.department_name, COUNT(*) AS bookings
FROM fact_room_booking f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_department dep ON dep.department_key = f.department_key
WHERE d.year = 2024 AND d.quarter = 1
GROUP BY dep.department_name ORDER BY bookings DESC;

-- Q12: DICE: Engineering digital downloads in March 2024 by resource type and user type
SELECT r.resource_type, ut.user_type, SUM(f.download_count) AS downloads
FROM fact_digital_usage f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_department dep ON dep.department_key = f.department_key
JOIN dim_resource r ON r.resource_key = f.resource_key
JOIN dim_user_type ut ON ut.user_type_key = f.user_type_key
WHERE dep.department_name = 'Engineering' AND d.year_month = '2024-03'
GROUP BY r.resource_type, ut.user_type ORDER BY downloads DESC;

-- Q13: PIVOT: resource types (columns) across departments (rows)
SELECT dep.department_name,
       SUM(CASE WHEN r.resource_type = 'Book'    THEN u.v END) AS books_borrowed,
       SUM(CASE WHEN r.resource_type = 'E-book'  THEN u.v END) AS ebook_downloads,
       SUM(CASE WHEN r.resource_type = 'Journal' THEN u.v END) AS journal_downloads,
       SUM(CASE WHEN r.resource_type = 'Article' THEN u.v END) AS article_downloads
FROM (SELECT department_key, resource_key, 1 AS v FROM fact_book_loan
      UNION ALL
      SELECT department_key, resource_key, download_count FROM fact_digital_usage) u
JOIN dim_resource r ON r.resource_key = u.resource_key
JOIN dim_department dep ON dep.department_key = u.department_key
WHERE dep.department_key > 0
GROUP BY dep.department_name ORDER BY dep.department_name;
-- Q14: Monthly usage trends: loans vs downloads vs room bookings
SELECT d.year_month,
       SUM(CASE WHEN u.service = 'Loans'     THEN u.n END) AS loans,
       SUM(CASE WHEN u.service = 'Downloads' THEN u.n END) AS downloads,
       SUM(CASE WHEN u.service = 'Bookings'  THEN u.n END) AS bookings
FROM (SELECT checkout_date_key AS date_key, 'Loans' AS service, 1 AS n FROM fact_book_loan
      UNION ALL
      SELECT date_key, 'Downloads', download_count FROM fact_digital_usage
      UNION ALL
      SELECT date_key, 'Bookings', 1 FROM fact_room_booking) u
JOIN dim_date d ON d.date_key = u.date_key
GROUP BY d.year_month ORDER BY d.year_month;
-- Q15: Undergraduate vs graduate loans
SELECT s.student_level, COUNT(*) AS loans, ROUND(AVG(f.loan_days), 1) AS avg_loan_days
FROM fact_book_loan f
JOIN dim_student s ON s.student_key = f.student_key
WHERE s.student_key > 0
GROUP BY s.student_level;
-- Q16: Heat map data: room bookings by day of week and time block
SELECT ((CAST(strftime('%w', d.full_date) AS INTEGER) + 6) % 7 + 1) || '-' || d.day_name AS day,
       t.slot_name, COUNT(*) AS bookings
FROM fact_room_booking f
JOIN dim_date d     ON d.date_key = f.date_key
JOIN dim_timeslot t ON t.timeslot_key = f.timeslot_key
GROUP BY day, t.slot_name;

-- Q17: Bookings per room, with purposes
SELECT rm.room_code, COUNT(*) AS bookings, ROUND(AVG(f.duration_hours), 2) AS avg_hours,
       SUM(f.purpose = 'Study') AS study,
       SUM(f.purpose = 'Group Project') AS group_project,
       SUM(f.purpose = 'Meeting') AS meeting
FROM fact_room_booking f
JOIN dim_room rm ON rm.room_key = f.room_key
GROUP BY rm.room_code ORDER BY bookings DESC;

-- Q18: Daily room bookings, last 60 days of data
SELECT d.full_date, COUNT(*) AS bookings
FROM fact_room_booking f
JOIN dim_date d ON d.date_key = f.date_key
WHERE d.full_date > date((SELECT MAX(d2.full_date) FROM fact_room_booking f2
                          JOIN dim_date d2 ON d2.date_key = f2.date_key), '-60 day')
GROUP BY d.full_date ORDER BY d.full_date;

-- Q19: Booking purpose
SELECT purpose, COUNT(*) AS bookings FROM fact_room_booking GROUP BY purpose;