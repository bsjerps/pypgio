-----------------------------------------------------------------------------
-- Title       : create_db.sql
-- Description : Create the initial schema for pypgio
-- Author      : Bart Sjerps <bart@dirty-cache.com>
-- License     : GPLv3+
-----------------------------------------------------------------------------

-- Log in on Postgres as postgres (admin) user using psql

-- As user postgres
create user pgio with encrypted password 'pgio';
alter user pgio createdb;

-- Optional - create tablespace
create tablespace pgio location '/pgiodata';
grant all privileges on tablespace pgio to pgio;

-- Optional - extra privileges
grant execute on function pg_stat_reset to pgio;

-- Switch user
set role pgio;

-- As user pgio
create database pgio;
