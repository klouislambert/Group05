# Data Quality Report

Before = raw source files. After = loaded warehouse.

| Source | Metric | Before | After |
|---|---|---|---|
| Book loans | Rows | 3025 | 3000 |
| Book loans | Duplicate rows | 25 | 0 |
| Book loans | Department spellings | 20 | 7 |
| Book loans | Empty department | 106 | 0 |
| Book loans | Dates not in YYYY-MM-DD | 872 | 0 |
| Book loans | Empty ReturnDate (kept, not returned yet) | 487 | 483 |
| Digital downloads | Rows | 2100 | 2100 |
| Digital downloads | Resource type spellings | 6 | 3 |
| Digital downloads | Faculty spellings | 20 | 7 |
| Digital downloads | DownloadCount with commas | 20 | 0 |
| Digital downloads | Missing Duration_Minutes (kept as NULL) | 500 | 500 |
| Room bookings | Rows | 1540 | 1500 |
| Room bookings | Duplicate rows | 40 | 0 |
| Room bookings | Room number spellings | 30 | 10 |
| Room bookings | Time slot spellings | 11 | 3 |
| Room bookings | Walk-ins without StudentID (kept as Unknown) | 126 | 121 |
| Warehouse | Broken foreign keys | n/a | 0 |
