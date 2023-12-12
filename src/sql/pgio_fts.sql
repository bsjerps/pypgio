-----------------------------------------------------------------------------
-- Title       : pgio_fts.sql
-- Description : Run Full Table Scans on PGIO tables
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION pgio_fts(v_mytab VARCHAR, v_runtime_secs BIGINT) 
RETURNS pgio_return LANGUAGE plpgsql
AS $$
DECLARE
record     pgio_return%rowtype;
v_end_time TIMESTAMP WITHOUT TIME ZONE;
v_before   TIMESTAMP WITHOUT TIME ZONE; 
v_count    BIGINT  := 0;
v_tm_delta NUMERIC := 0.0;

BEGIN
	record.mypid                = pg_backend_pid();
	record.sql_selects          = 0;
	record.sql_updates          = 0;
	record.sql_select_max_tm	= 0.0;
	record.sql_update_max_tm	= 0.0;
	record.loop_iterations      = 0;
	record.select_blk_touch_cnt = 0;
	record.update_blk_touch_cnt = 0;
	
	v_end_time := clock_timestamp() + (v_runtime_secs || ' seconds')::interval;

	WHILE ( clock_timestamp()::timestamp < v_end_time ) LOOP
		v_before := clock_timestamp();
		EXECUTE 'SELECT COUNT(scratch) FROM ' || v_mytab INTO v_count;
		v_tm_delta := cast(extract(epoch from (clock_timestamp() - v_before)) AS NUMERIC(12,8));
		IF ( v_tm_delta > record.sql_select_max_tm ) THEN
			record.sql_select_max_tm := v_tm_delta;
		END IF;
		record.loop_iterations      = record.loop_iterations + 1;
		record.sql_selects          = record.sql_selects + 1;
		record.select_blk_touch_cnt = record.select_blk_touch_cnt + v_count;
	END LOOP;
	RETURN record;
END;
$$
;