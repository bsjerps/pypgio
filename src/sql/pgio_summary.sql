-----------------------------------------------------------------------------
-- Title       : pgio_summary.sql
-- Description : Show results summary
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

SELECT count(*)             threads
, sum(loop_iterations)      loops
, sum(sql_selects)          selects
, sum(sql_updates)          updates
, max(sql_select_max_tm)    max_select
, max(sql_update_max_tm)    max_update
, sum(select_blk_touch_cnt) blocks_selected
, sum(update_blk_touch_cnt) blocks_updated
FROM pgio_table_stats