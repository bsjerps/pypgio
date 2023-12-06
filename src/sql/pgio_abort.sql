-----------------------------------------------------------------------------
-- Title       : pgio_abort.sql
-- Description : Kill runaway pypgio sessions
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

SELECT pid
, datname
, usename
, application_name
, pg_cancel_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
AND application_name ~ 'pgio_\d+'
