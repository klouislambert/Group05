-- Masked student view: analysts see STU-****-001 instead of STU-2024-001
CREATE VIEW IF NOT EXISTS vw_student_masked AS
SELECT student_key,
       CASE WHEN student_id = 'UNKNOWN' THEN 'UNKNOWN'
            ELSE 'STU-****-' || substr(student_id, 10) END AS student_id,
       student_level,
       department_key
FROM dim_student;

-- Department head view: Engineering head sees only Engineering loans
CREATE VIEW IF NOT EXISTS vw_head_engineering_loans AS
SELECT f.*
FROM fact_book_loan f
JOIN dim_department d ON d.department_key = f.department_key
WHERE d.department_name = 'Engineering';