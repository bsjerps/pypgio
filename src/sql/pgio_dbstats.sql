-----------------------------------------------------------------------------
-- Title       : pgio_dbstats.sql
-- Description : Report database IO statistics over the last iteration 
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

SELECT to_char(last_stamp, 'HH24:MI:SS') timestamp
, round(runtime,2) runtime
, hits
, reads
, returned
, fetched
, updated
, 100*reads/returned "read %"
, round(reads/runtime)      "reads/s"
, round(fetched/runtime)    "fetch/s"
, round(updated/runtime)    "writes/s"
FROM (
	SELECT ts
	, max(ts) OVER () last_stamp
	, extract(seconds FROM ts - lag(ts) OVER ()) runtime
	, blks_hit     - lag(blks_hit)     OVER ()   hits     -- Number of times disk blocks were found already in the db buffer cache
	, blks_read    - lag(blks_read)    OVER ()   reads    -- Number of disk blocks read in this database
	, tup_returned - lag(tup_returned) OVER ()   returned -- Number of live rows fetched by sequential scans and index entries returned by index scans in this database
	, tup_fetched  - lag(tup_fetched)  OVER ()   fetched  -- Number of live rows fetched by index scans in this database
	, tup_updated  - lag(tup_updated)  OVER ()   updated  -- Number of rows updated by queries in this database
	FROM pgio_dbstats
	ORDER BY ts
) t
WHERE ts = last_stamp
