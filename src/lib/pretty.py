"""
pretty.py - Pretty print a table (header + rows)
Copyright (c) 2023 - Bart Sjerps <bart@dirty-cache.com>
License: GPLv3+
"""

from prettytable import PrettyTable

def pretty(args, header, data, title=None):
    """
    Print a header and array of rows in pretty format
    If args.tabs is set, print in tab separated format
    If args.nohead is set, print tab format without header
    title - adds a title to the table
    """
    if args.tabs:
        if not args.nohead:
            print('\t'.join(header))
        for r in data:
            print('\t'.join([str(x) for x in r]))
        print()
    else:    
        tbl = PrettyTable()
        if title is not None:
            tbl.title = title
        tbl.field_names = header
        tbl.align = "l"
        for r in data:
            tbl.add_row(r)
        print(tbl)
        print()
