BEGIN TRANSACTION;

-- Create new table with correct primary key
CREATE TABLE IF NOT EXISTS sessions_new (
  mac TEXT PRIMARY KEY,
  first_seen REAL,
  last_seen REAL
);

-- Copy existing data (if any)
INSERT INTO sessions_new (mac, first_seen, last_seen)
SELECT mac, first_seen, last_seen FROM sessions;

-- Drop old table
DROP TABLE sessions;

-- Rename new table to original name
ALTER TABLE sessions_new RENAME TO sessions;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS devices (
    mac TEXT PRIMARY KEY,
    roll_no TEXT,
    name TEXT
);

COMMIT;
