-----------------------------------------------------------------------------
-- Title       : pgio_destroy.sql
-- Description : Destroys the master pgio tables/functions/types
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

DROP TABLE IF EXISTS pgio_seed;
DROP TABLE IF EXISTS pgio_table_stats;
DROP TABLE IF EXISTS pgio_dbstats;
DROP FUNCTION IF EXISTS mypgio(varchar, int4, int8, int8, int4, int4);
DROP FUNCTION IF EXISTS pgio_fts(varchar, int8);
DROP FUNCTION IF EXISTS pgio_get_random_number(int8, int8);
DROP TYPE IF EXISTS pgio_return;
