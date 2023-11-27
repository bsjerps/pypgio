-----------------------------------------------------------------------------
-- Title       : pgio_details.sql
-- Description : Show results per thread
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

SELECT pid
, table_name       "table"
, round(runtime,2) "runtime"
, work_unit || ':' || update_unit  "units"
, loops
, selects
, updates
, round(max_select,4)              "max_select"
, round(max_update,4)              "max_update"
, blocks_selected                  "blks_selected"
, blocks_updated                   "blks_updated"
, round(blocks_selected/runtime) "read/s"
, round(blocks_updated/runtime)  "write/s"
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
	, select_blk_touch_cnt  blocks_selected
	, update_blk_touch_cnt  blocks_updated
	FROM pgio_table_stats
	ORDER BY pid
)
