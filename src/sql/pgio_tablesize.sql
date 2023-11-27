-----------------------------------------------------------------------------
-- Title       : pgio_tablesize.sql
-- Description : Report the sizes of the pgio_tables
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

SELECT table_schema schema
, tablespace
, table_name "table"
, pg_size_pretty(pg_table_size(table_schema || '.' || table_name)) "size"
FROM information_schema.tables
JOIN pg_tables ON schemaname = table_schema AND tablename = table_name
WHERE table_name ~ 'pgio\d+'
ORDER BY table_name