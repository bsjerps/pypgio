-----------------------------------------------------------------------------
-- Title       : pgio_summary.sql
-- Description : Show results summary
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

SELECT 'Total' pid
, tables
, runtime
, work_unit || ':' || update_unit  "units"
, loops
, selects
, updates
, ROUND(max_select,4)          "max_select"
, ROUND(max_update,4)          "max_update"
, blks_selected
, blks_updated
, ROUND(blks_selected/runtime) "read/s"
, ROUND(blks_updated/runtime)  "write/s"
FROM (
	SELECT COUNT(*)             threads
	, COUNT(table_name)         tables
    , ROUND(extract(epoch FROM MAX(ts_end) - MIN(ts_start)),2) runtime
	, MAX(work_unit)            work_unit
	, MAX(update_unit)          update_unit
	, SUM(loop_iterations)      loops
	, SUM(sql_selects)          selects
	, SUM(sql_updates)          updates
	, MAX(sql_select_max_tm)    max_select
	, MAX(sql_update_max_tm)    max_update
	, SUM(select_blk_touch_cnt) blks_selected
	, SUM(update_blk_touch_cnt) blks_updated
	, TO_CHAR(MIN(ts_start), 'HH24:MI:SS') ts_start
	, TO_CHAR(MAX(ts_end), 'HH24:MI:SS')   ts_end
	FROM pgio_table_stats
) t
