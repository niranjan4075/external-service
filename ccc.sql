BEGIN;

-- 1) Prevent anyone from reading/writing peripherals while we swap data
LOCK TABLE peripherals IN ACCESS EXCLUSIVE MODE;

-- 2) Backup current peripherals (structure + data)
-- Change the suffix if you want a different backup name
DROP TABLE IF EXISTS peripherals_backup_20260108;
CREATE TABLE peripherals_backup_20260108 AS
SELECT * FROM peripherals;

-- 3) Clear data from peripherals (table remains)
DELETE FROM peripherals;

-- 4) Load new data from peripherals_test
INSERT INTO peripherals
SELECT * FROM peripherals_test;

-- 5) Reset sequence for peripheralid (safe for SERIAL-based PK)
SELECT setval(
  pg_get_serial_sequence('peripherals','peripheralid'),
  (SELECT COALESCE(MAX(peripheralid), 1) FROM peripherals),
  true
);

COMMIT;

-- 6) Validate counts + quick check
SELECT COUNT(*) AS peripherals_count FROM peripherals;
SELECT COUNT(*) AS peripherals_test_count FROM peripherals_test;
SELECT COUNT(*) AS peripherals_backup_count FROM peripherals_backup_20260108;

SELECT * FROM peripherals ORDER BY peripheralid LIMIT 10;
