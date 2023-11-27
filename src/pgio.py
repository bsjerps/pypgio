#!/usr/bin/env python3
"""
pgio.py - Main file for PyPGIO - An IO generator for PostgreSQL based on the original pgio and SLOB
Copyright (c) 2023 - Bart Sjerps <bart@dirty-cache.com>
Based on the original PGIO by Kevin Closson - see https://github.com/therealkevinc/pgio
License: GPLv3+
"""

import sys
sys.dont_write_bytecode = True

import os, argparse, logging
from time import sleep
from datetime import datetime
from threading import Thread, Event
from queue import Queue

from lib.pgio_functions import install, printversion

# Prompt user to install or activate when needed
if not sys.prefix != sys.base_prefix:
    homedir = os.path.expanduser('~')
    envdir  = os.path.join(homedir, 'pgio_venv')
    if not os.path.isdir(envdir):
        install()
        print("# First run pgio installer:\n\nbash install_pgio\n")
    else:
        print("# Please activate the virtual environment:\n\nsource ~/pgio_venv/bin/activate\nsource ~/pgio_venv/bin/complete_pgio\n")
    sys.exit(1)

try:
    from psycopg import OperationalError, DatabaseError
    from lib.pretty import pretty
except ImportError as e:
    print(f'# Import failed: {e.name}')
    print(f'# Please install {e.name}:')
    print(f'pip install {e.name}')
    sys.exit(20)

from lib.database import Database
from lib.config import Config

logging.basicConfig(level=logging.INFO,
    format="%(levelname)-8s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

def nt2str(nt):
    """Named tuple to printable string"""
    words = [f"{k}={str(getattr(nt, k))}" for k in nt._fields]
    return ' '.join(words)

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
    pretty(args, head, data)

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
            logging.info(f"Worker {n} - Creating table {table_name}")
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

        db.run_task(table_name, config.update_pct, args.runtime, config.scale, config.work_unit, config.update_unit, datetime.now())

    except DatabaseError as e:
        logging.error(e)

def setup(args, config):
    db = Database(config)
    db.schema()
    if config.tablespace:
        db.default_tablespace(config.tablespace)

    # Drop extra tables
    logging.info(f'Purging excess tables...')
    for t in db.script('pgio_purgelist.sql', (config.schemas,)):
        db.drop_table(t[0])

    logging.info(f'Creating seed table with {config.scale} rows')
    t_start = datetime.now()
    db.create_seed(config.scale)
    t_end   = datetime.now()
    runtime = (t_end - t_start).total_seconds()
    logging.info(f'Seed table created in {round(runtime,2)} seconds')

    # Queue with table names for distributing tasks to the create threads
    queue = Queue()
    for i in range(config.schemas):
        table_name = f'pgio{i}'
        queue.put(table_name)

    # Create and start the create threads
    threads = []
    t_start = datetime.now()
    for j in range(args.threads):
        proc = Thread(target=create_thread, name=f'creator', args=(j, args, config, queue))
        proc.start()
        threads.append(proc)

    logging.info(f"Started {len(threads)} threads...")

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    t_end   = datetime.now()
    runtime = (t_end - t_start).total_seconds()
    logging.info(f'Data tables created in {round(runtime,2)} seconds')

def report(args, config):
    db = Database(config)
    if args.verbose:
        head, data = db.report('pgio_details.sql')
        pretty(args, head, data, 'Results per thread')

        head, data = db.report('pgio_summary.sql')
        pretty(args, head, data, 'Summary')

    head, data = db.report('pgio_dbstats.sql')
    pretty(args, head, data, 'Database I/O stats')

def runit(args, config):
    db = Database(config)
    db.execute('TRUNCATE TABLE pgio_table_stats')
    db.execute('TRUNCATE TABLE pgio_dbstats')

    buffers = db.fetchone("SELECT setting buffers, unit, setting::int/128 size_mb FROM pg_settings WHERE name = 'shared_buffers'")
    t_start = datetime.now()

    # Do not use more schemas than available
    schemas = min(config.schemas, db.schemas)
    if args.threads > schemas:
        raise ValueError(f"Cannot use more threads than schemas")

    logging.info(f"Date:           {t_start.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Server:         {db.conn.info.host}")
    logging.info(f"Database:       {db.conn.info.dbname}")
    logging.info(f"Shared Buffers: {buffers.size_mb} (MiB)")
    logging.info(f"Runtime:        {args.runtime}")
    logging.info(f"Workers:        {args.threads}")
    logging.info(f"Update %:       {config.update_pct}")
    logging.info(f"Work_unit:      {config.work_unit}")
    logging.info(f"Update_unit:    {config.update_unit}")

    logging.info(f"Testing {schemas} schemas with {args.threads} thread(s) accessing {config.size} ({config.scale} blocks) of each schema.")
    logging.info(f"Launching sessions. {config.schemas} schema(s) will be accessed by {args.threads} thread(s) total")

    threads = []
    syncwait = Event()

    for i in range(args.threads):
        schema_num = i % schemas
        proc = Thread(target=worker_thread, args=(schema_num, args, config, syncwait))
        proc.start()
        threads.append(proc)

    db.update_stats()
    syncwait.set()
    logging.info(f"Started {len(threads)} threads...")
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

    parser_destroy.set_defaults(func=destroy)
    parser_config.set_defaults(func=configure)
    parser_setup.set_defaults(func=setup)
    parser_list.set_defaults(func=tablesizes)
    parser_run.set_defaults(func=runit)
    parser_report.set_defaults(func=report)
    parser_abort.set_defaults(func=abort)

    parser_config.set_defaults(func=configure)
    parser_config.add_argument('--defaults', action='store_true',     help='Default settings')
    parser_config.add_argument('--dbhost',     metavar='hostname',    help='Database host')
    parser_config.add_argument('--dbname',     metavar='database',    help='Database name')
    parser_config.add_argument('--dbuser',     metavar='user',        help='Database user')
    parser_config.add_argument('--dbpass',     metavar='password',    help='Database password')
    parser_config.add_argument('--dbport',     metavar='port',        help='Database port', type=int)
    parser_config.add_argument('--remote',     metavar='user@host',   help='Remote SSH destination')
    parser_config.add_argument('--update_pct', metavar='pct',         help='Update percentage', type=int)
    parser_config.add_argument('--scale',      metavar="<size>M|G|T", help="Schema size")
    parser_config.add_argument('--schemas',    metavar="n", type=int, help="Number of user schemas")
    parser_config.add_argument('--work_unit',  metavar="n", type=int, help="Work unit")
    parser_config.add_argument('--update_unit',metavar="n", type=int, help="Update unit")
    parser_config.add_argument('--tablespace', metavar='name',        help="Tablespace")

    parser_setup.add_argument('threads', metavar="<n>", type=int, nargs='?', default=1, help="Number of workers for schema creation")
    parser_report.add_argument('-v', '--verbose', help="Extra details", action="store_true")

    parser_run.add_argument('-v', '--verbose', help="Extra details", action="store_true")
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
        logging.error(f"Database error: {e}")
        if args.debug:
            logging.exception(e)
    except ValueError as e:
        logging.error(e)
        if args.debug:
            logging.exception(e)
        sys.exit(10)

if __name__ == '__main__':
    main()