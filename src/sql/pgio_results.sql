-----------------------------------------------------------------------------
-- Title       : pgio_details.sql
-- Description : Show results per thread
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

SELECT pid
, table_name       "table"
, ROUND(runtime,2) "runtime"
, work_unit || ':' || update_unit  "units"
, loops
, selects
, updates
, ROUND(100*updates::numeric/loops,2) "upd %"
, ROUND(max_select,4)                 "max_select"
, ROUND(max_update,4)                 "max_update"
, selected                            "selected"
, updated                             "updated"
, ROUND(selected/runtime)             "read/s"
, ROUND(updated/runtime)              "write/s"
, ROUND((selected+updated)/runtime)   "iops"
, ROUND(100*updated/NULLIF(selected+updated,0),2) "write %"
FROM (
	SELECT mypid pid
	, table_name            
	, extract(epoch FROM ts_end - ts_start) runtime
	, work_unit             
	, update_unit
	, loop_iterations       loops
	, sql_selects           selects
	, sql_updates           updates
	, sql_select_max_tm     max_select
	, sql_update_max_tm     max_update
	, select_blk_touch_cnt  selected
	, update_blk_touch_cnt  updated
	FROM pgio_table_stats
	ORDER BY pid
) t
