-----------------------------------------------------------------------------
-- Title       : pgio_seed.sql
-- Description : Create the seed table for pgio
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- Original    : Kevin Closson (https://github.com/therealkevinc/pgio)
-- License     : GPLv3+
-----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pgio_seed AS
SELECT mykey::bigint
, (random()*1000000000)::bigint AS scratch
, repeat('X', 1024)::char(1024) AS filler 
FROM generate_series(1,%s) AS mykey
ORDER BY scratch