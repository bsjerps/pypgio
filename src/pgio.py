"""
pgio.py - Main file for PyPGIO - An IO generator for PostgreSQL based on the original pgio and SLOB
Copyright (c) 2024 - Bart Sjerps <bart@dirty-cache.com>
Based on the original PGIO by Kevin Closson - see https://github.com/therealkevinc/pgio
License: GPLv3+
"""

import os, sys, argparse, logging
from datetime import datetime
from threading import Thread, Event
from queue import Queue
from pkgutil import get_data

sys.dont_write_bytecode = True

logging.basicConfig(level=logging.INFO,
    format="%(levelname)-8s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

try:
    from psycopg import OperationalError, DatabaseError
    from lib.pretty import Pretty
    from lib.database import Database
    from lib.config import Config, printversion, versioninfo

except ImportError as e:
    if sys.stdout.isatty():
        logging.error(e)

    modpath = os.path.dirname(__file__)

    if sys.prefix == sys.base_prefix:
        if not os.path.exists(os.path.join(os.path.expanduser('~'),'.virtualenvs', 'pgio')):
            print('# Install pgio virtual environment:')
            print('python3 -m venv $HOME/.virtualenvs/pgio')
            print('$HOME/.virtualenvs/pgio/bin/pip install psycopg prettytable')

        else:
            if sys.stdout.isatty():
                print('# Not running from virtual environment. run:')
                print('source <(pypgio)')
            else:
                print('source $HOME/.virtualenvs/pgio/bin/activate')


    sys.exit(10)

def complete(args, config):
    """Dump the bash_completions on stdout"""
    txt = get_data('install', 'complete_pgio')
    print(txt.decode())

def destroy(args, config):
    """Delete all pgio related stuff from the database"""
    db = Database(config)
    db.destroy()

def abort(args, config):
    db = Database(config)
    db.script('pgio_abort.sql')

def configure(args, config):
    config.configure(args)

def tablesizes(args, config):
    db = Database(config)
    head, data = db.report('pgio_tablesize.sql')
    pretty = Pretty(head)
    pretty.rows(data)
    pretty.print(args)

def create_thread(n, args, config, queue):
    """Thread for creating and loading a data table"""
    try:
        db = Database(config, name=f'create_{n}')
        if config.tablespace:
            db.default_tablespace(config.tablespace)

        while True:
            if queue.empty():
                break
            table_name = queue.get(timeout=10)
            logging.info("Worker %s - Creating table %s", n, table_name)
            db.create_table(table_name)

    except DatabaseError as e:
        logging.error(e)

def worker_thread(schema_num, args, config, syncwait):
    """Thread for running one task against one tabletable"""
    try:
        db = Database(config, name=f'pgio_{schema_num}')
        table_name = f'pgio{schema_num}'

        if not syncwait.wait(timeout=3):
            logging.error("Timeout")
            sys.exit(1)

        if args.fts:
            db.run_fts(table_name, args.runtime, datetime.now())

        else:
            db.run_task(table_name, config.update_pct, args.runtime, config.scale, config.work_unit, config.update_unit, datetime.now())

    except DatabaseError as e:
        logging.error(e)

def setup(args, config):
    db = Database(config)
    db.schema()
    if config.tablespace:
        db.default_tablespace(config.tablespace)

    # Drop extra tables
    logging.info('Purging excess tables...')
    for t in db.script('pgio_purgelist.sql', (config.schemas,)):
        db.drop_table(t[0])

    logging.info('Creating seed table with %s rows', config.scale)
    t_start = datetime.now()
    db.create_seed(config.scale)
    t_end   = datetime.now()
    runtime = (t_end - t_start).total_seconds()
    logging.info('Seed table created in %s seconds', round(runtime,2))

    # Queue with table names for distributing tasks to the create threads
    queue = Queue()
    for i in range(config.schemas):
        table_name = f'pgio{i}'
        queue.put(table_name)

    # Create and start the create threads
    threads = []
    t_start = datetime.now()
    for j in range(args.threads):
        proc = Thread(target=create_thread, name='creator', args=(j, args, config, queue))
        proc.start()
        threads.append(proc)

    logging.info("Started %s threads...", len(threads))

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    t_end   = datetime.now()
    runtime = (t_end - t_start).total_seconds()
    logging.info('Data tables created in %s seconds', round(runtime, 2))

def report(args, config):
    db = Database(config)
    if args.verbose:
        head, data = db.report('pgio_results.sql')
        t = Pretty(head, 'Results')
        t.rows(data)
        t.linebreak()

        head, data = db.report('pgio_summary.sql')
        t.data.append(data[-1])
        t.print(args)

    head, data = db.report('pgio_dbstats.sql')
    t = Pretty(head, 'Database I/O stats')
    t.rows(data)
    t.print(args)

def runit(args, config):
    db = Database(config, name='pgio_runner')
    db.execute('TRUNCATE TABLE pgio_table_stats')
    db.execute('TRUNCATE TABLE pgio_dbstats')

    buffers = db.fetchone("SELECT setting buffers, unit, setting::int/128 size_mb FROM pg_settings WHERE name = 'shared_buffers'")
    t_start = datetime.now()

    # Do not use more schemas than available
    schemas = min(config.schemas, db.schemas)
    if args.threads > schemas:
        raise ValueError("Cannot use more threads than schemas (unsupported)")

    logging.info("PyPGIO %s", versioninfo['version'])

    logging.info("Date:           %s", t_start.strftime('%Y-%m-%d %H:%M:%S'))
    logging.info("Server:         %s", db.conn.info.host)
    logging.info("Database:       %s", db.conn.info.dbname)
    logging.info("Shared Buffers: %s (MiB)", buffers.size_mb)
    logging.info("Runtime:        %s", args.runtime)
    logging.info("Workers:        %s", args.threads)
    logging.info("Update %%:       %s", config.update_pct)
    logging.info("Work_unit:      %s", config.work_unit)
    logging.info("Update_unit:    %s", config.update_unit)

    logging.info("Testing %s thread(s) accessing %s (%s blocks) each.", args.threads, config.size, config.scale)

    threads = []
    syncwait = Event()

    for i in range(args.threads):
        schema_num = i % schemas
        proc = Thread(target=worker_thread, args=(schema_num, args, config, syncwait))
        proc.start()
        threads.append(proc)

    db.update_stats()
    syncwait.set()
    logging.info("Started %s threads...", len(threads))
    for thread in threads:
        thread.join()
    db.update_stats()

    report(args, config)

def main():
    formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=40)
    parser = argparse.ArgumentParser()

    parser.add_argument('-D', '--debug',   help="Debugging info", action="store_true")
    parser.add_argument('-t', '--tabs',    help="TAB separated output", action="store_true")
    parser.add_argument('-n', '--nohead',  help="No heading (with --tabs)", action="store_true")
    parser.add_argument('-V', '--version', help="Show version and copyright", action="store_true")

    subparsers      = parser.add_subparsers(title='commands', dest='cmd')
    parser_destroy  = subparsers.add_parser('destroy',   help='Destroy PGIO data/config')
    parser_config   = subparsers.add_parser('configure', formatter_class=formatter, help='Configure settings')
    parser_setup    = subparsers.add_parser('setup',     help='Setup tables')
    parser_list     = subparsers.add_parser('list',      help='List tablesizes')
    parser_run      = subparsers.add_parser('run',       help='run benchmark')
    parser_report   = subparsers.add_parser('report',    help='Report')
    parser_abort    = subparsers.add_parser('abort',     help='Cancel running jobs')
    parser_complete = subparsers.add_parser('complete',  help='Dump bash completion file')

    parser_destroy.set_defaults(func=destroy)
    parser_config.set_defaults(func=configure)
    parser_setup.set_defaults(func=setup)
    parser_list.set_defaults(func=tablesizes)
    parser_run.set_defaults(func=runit)
    parser_report.set_defaults(func=report)
    parser_abort.set_defaults(func=abort)
    parser_complete.set_defaults(func=complete)

    parser_config.set_defaults(func=configure)
    parser_config.add_argument('--defaults', action='store_true',     help='Default settings')
    parser_config.add_argument('--dbhost',     metavar='hostname',    help='Database host')
    parser_config.add_argument('--dbname',     metavar='database',    help='Database name')
    parser_config.add_argument('--dbuser',     metavar='user',        help='Database user')
    parser_config.add_argument('--dbpass',     metavar='password',    help='Database password')
    parser_config.add_argument('--dbport',     metavar='port',        help='Database port', type=int)
    parser_config.add_argument('--update_pct', metavar='pct',         help='Update percentage', type=int)
    parser_config.add_argument('--scale',      metavar="<size>M|G|T", help="Schema size")
    parser_config.add_argument('--schemas',    metavar="n", type=int, help="Number of user schemas")
    parser_config.add_argument('--work_unit',  metavar="n", type=int, help="Work unit")
    parser_config.add_argument('--update_unit',metavar="n", type=int, help="Update unit")
    parser_config.add_argument('--tablespace', metavar='name',        help="Tablespace")

    parser_setup.add_argument('threads', metavar="<n>", type=int, nargs='?', default=1, help="Number of workers for schema creation")
    parser_report.add_argument('-v', '--verbose', help="Extra details", action="store_true")

    parser_run.add_argument('-v', '--verbose', help="Extra details", action="store_true")
    parser_run.add_argument('-f', '--fts', help="Full Table Scans", action="store_true")
    parser_run.add_argument('runtime', metavar='<runtime>', type=int, help="Runtime in seconds")
    parser_run.add_argument('threads', metavar="<threads>", type=int, help="Number of workers per schema")

    args = parser.parse_args()

    if args.version:
        printversion()
        sys.exit()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        config = Config()
        if args.cmd is None:
            tablesizes(args, config)
        else:
            args.func(args, config)
    except KeyboardInterrupt:
        logging.warning('Aborted, exiting...')
    except OperationalError as e:
        logging.error("Reading database failed. Try --setup")
        if args.debug:
            logging.exception(e)
    except DatabaseError as e:
        logging.error("Database error: %s", e)
        if args.debug:
            logging.exception(e)
    except ValueError as e:
        logging.error(e)
        if args.debug:
            logging.exception(e)
        sys.exit(10)

if __name__ == '__main__':
    main()
