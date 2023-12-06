-----------------------------------------------------------------------------
-- Title       : pgio_purgelist.sql
-- Description : Shows the excess tables to be deleted after changing schemas
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

SELECT table_name
FROM (
	SELECT table_name, LTRIM(table_name,'pgio')::INT table_num
	FROM information_schema.tables
	WHERE table_schema = 'public'
	AND table_name ~ 'pgio\d+'
) t
WHERE table_num >= %s
ORDER BY table_num
