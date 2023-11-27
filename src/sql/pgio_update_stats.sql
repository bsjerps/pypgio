-----------------------------------------------------------------------------
-- Title       : pgio_update_stats.sql
-- Description : Save current DB I/O stats
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

INSERT INTO pgio_dbstats(blks_hit, blks_read, tup_returned, tup_fetched, tup_updated)
SELECT blks_hit, blks_read,tup_returned,tup_fetched,tup_updated
FROM pg_stat_database
WHERE datname = %s
