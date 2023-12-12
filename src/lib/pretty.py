"""
pretty.py - Pretty print a table (header + rows)
Copyright (c) 2023 - Bart Sjerps <bart@dirty-cache.com>
License: GPLv3+
"""

from prettytable import PrettyTable

class Pretty():
    def __init__(self, header, title=None):
        self.header = header
        self.data = []
        self.breaks = []
        self.tbl = PrettyTable()
        self.tbl.field_names = header
        if title:
            self.tbl.title = title

    def rows(self, data):
        self.data = data

    def linebreak(self):
        self.breaks.append(len(self.data))
    
    def print(self, args):
        if args.tabs:
            if not args.nohead:
                print('\t'.join(self.header))
            for r in self.data:
                print('\t'.join([str(x) for x in r]))
        else:
            for i, r in enumerate(self.data):
                if i+1 in self.breaks:
                    try:
                        self.tbl.add_row(r, divider=True)
                    except TypeError:
                        self.tbl.add_row(r)
                        self.tbl.add_row(['---'] * len(r))
                else:
                    self.tbl.add_row(r)
            self.tbl.align = "r"
            print(self.tbl)
        print()
