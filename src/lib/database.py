"""
database.py - Database class/functions for pypgio
Copyright (c) 2023 - Bart Sjerps <bart@dirty-cache.com>
License: GPLv3+
"""

import psycopg, logging
from pkgutil import get_data

from psycopg.sql import SQL, Identifier, Literal
from psycopg.rows import namedtuple_row

class Database():
    def __init__(self, config, name=None):
        try:
            self.conn = psycopg.connect(host=config.dbhost, dbname=config.dbname, user=config.dbuser, password=config.dbpass, autocommit=True)
        except AttributeError as e:
            logging.error(e)
            raise ValueError(f'Bad database configuration {e}')
        except psycopg.OperationalError as e:
            raise ValueError(f'Connecting to database failed: {e}')
        if name:
            self.conn.execute(SQL("SET application_name TO {}").format(name))

    def getscript(self, name):
        return get_data('sql', name).decode()

    def schema(self):
        for file in ('pgio_schema.sql', 'pgio.sql', 'pgio_get_rand.sql'):
            data = self.getscript(file)
            sql = SQL(data).format(table=Identifier('seed'))
            with self.conn.transaction(), self.conn.cursor() as cur:
                cur.execute(sql)

    def execute(self, sql):
        return self.conn.execute(sql)

    def fetchone(self, sql, *args):
        with self.conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute(sql, *args)
            return cur.fetchone()

    def fetchall(self, sql, parameters=[]):
        with self.conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute(sql, parameters)
            return cur.fetchall()

    def script(self, name, *args):
        sql = self.getscript(name)
        with self.conn.cursor() as cur:
            cur.execute(sql, *args)
            return cur.fetchall()

    def report(self, name):
        sql = self.getscript(name)
        with self.conn.cursor() as cur:
            cur.execute(sql)
            header = [x.name for x in cur.description]
            data   = cur.fetchall()
            return header, data

    def default_tablespace(self, tablespace):
        self.execute(SQL("SET default_tablespace = {}").format(SQL(tablespace)))

    def tables(self):
        data = self.fetchall("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name LIKE 'pgio%%' ORDER BY 1")
        return [x.table_name for x in data]

    def update_stats(self):
        sql = self.getscript('pgio_update_stats.sql')
        with self.conn.cursor() as cur:
            cur.execute(sql, (self.conn.info.dbname,))

    def pgiostats(self):
        with self.conn.cursor() as cur:
            cur.execute('SELECT * FROM pgio_stats ORDER BY 1')
            head = [x.name for x in cur.description]
            data = cur.fetchall()
            return head, data

    @property
    def schemas(self):
        data = self.fetchone("SELECT count(*) n FROM information_schema.tables WHERE table_schema = 'public' AND table_name ~ 'pgio\d+' ")
        return data.n

    def create_seed(self, rowcount):
        sql = self.getscript('pgio_seed.sql')
        with self.conn.transaction(), self.conn.cursor() as cur:
            cur.execute('DROP TABLE IF EXISTS seed')
            cur.execute(sql, (rowcount,))

    def drop_table(self, table_name):
        with self.conn.transaction(), self.conn.cursor() as cur:
            cur.execute(SQL('DROP TABLE IF EXISTS {}').format(Identifier(table_name)))

    def create_table(self, table_name):
        self.drop_table(table_name)
        with self.conn.transaction(), self.conn.cursor() as cur:
            table = Identifier(table_name)
            index = Identifier(f'{table_name}_idx')
            cur.execute(SQL('CREATE TABLE {table} with (fillfactor=10) AS SELECT * FROM pgio_seed LIMIT 1').format(table=table))
            cur.execute(SQL('TRUNCATE TABLE {table}').format(table=table))
            cur.execute(SQL('CREATE INDEX IF NOT EXISTS {index} ON {table}(mykey)').format(table=table, index=index))
            cur.execute(SQL('INSERT INTO {table} SELECT * FROM pgio_seed').format(table=table))

    def destroy(self):
        with self.conn.transaction(), self.conn.cursor() as cur:
            logging.info('Dropping master data')
            sql = self.getscript('pgio_destroy.sql')
            cur.execute(sql)

            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name ~ 'pgio\d+' ORDER BY 1")
            tables = [x[0] for x in cur.fetchall()]
            for table_name in tables:
                logging.info(f'Dropping {table_name}')
                table = Identifier(table_name)
                cur.execute(SQL('DROP TABLE IF EXISTS {table}').format(table=table))

    def run_task(self, table_name, pct, run_tm, scale, work_unit, update_work_unit, ts):
        sql = SQL("SELECT * FROM mypgio({table_name}, {pct}, {run_tm}, {scale}, {work_unit}, {update_work_unit})").format(
            table_name       = Literal(table_name),
            pct              = Literal(pct),
            run_tm           = Literal(run_tm),
            scale            = Literal(scale),
            work_unit        = Literal(work_unit),
            update_work_unit = Literal(update_work_unit)
        )
        with self.conn.cursor() as cur:
            cur.execute(sql)
            data = cur.fetchone()

        with self.conn.transaction(), self.conn.cursor() as cur:
            sql = SQL(
                "INSERT INTO pgio_table_stats (mypid, loop_iterations, sql_selects, sql_updates, sql_select_max_tm, sql_update_max_tm, select_blk_touch_cnt, update_blk_touch_cnt, table_name, work_unit, update_unit, ts_start)\n"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)").format(
                    table_name = Literal(table_name
                )
            )
            cur.execute(sql, data + (table_name,work_unit, update_work_unit, ts))
