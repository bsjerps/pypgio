-----------------------------------------------------------------------------
-- Title       : pgio_schema.sql
-- Description : Create the initial schema for pgio
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pgio_table_stats(mypid INT PRIMARY KEY
, table_name           TEXT NOT NULL
, ts_start             TIMESTAMP NOT NULL
, ts_end               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
, work_unit            INTEGER NOT NULL
, update_unit          INTEGER NOT NULL
, loop_iterations      BIGINT NOT NULL
, sql_selects          BIGINT NOT NULL
, sql_updates          BIGINT NOT NULL
, sql_select_max_tm    NUMERIC NOT NULL
, sql_update_max_tm    NUMERIC NOT NULL
, select_blk_touch_cnt BIGINT NOT NULL
, update_blk_touch_cnt BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS pgio_dbstats(id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY
, ts           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
, blks_hit     BIGINT NOT NULL
, blks_read    BIGINT NOT NULL
, tup_returned BIGINT NOT NULL
, tup_fetched  BIGINT NOT NULL
, tup_updated  BIGINT NOT NULL
);
