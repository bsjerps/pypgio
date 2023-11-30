"""
config.py - Configuration management for pypgio
Copyright (c) 2023 - Bart Sjerps <bart@dirty-cache.com>
License: GPLv3+
"""

import os, json

versioninfo = {
    'author': "Bart Sjerps <info@dirty-cache.com>",
    'url': 'https://github.com/bsjerps/pypgio',
    'copyright': "Copyright 2023, Bart Sjerps",
    'license': "GPLv3+, https://www.gnu.org/licenses/gpl-3.0.html and Apache 2.0, http://www.apache.org/licenses/LICENSE-2.0",
    'version': "1.0.4"
}

def printversion():
    print("PyPGIO - An IO generator for PostgreSQL based on the original pgio and SLOB\n")
    print(f"Author:    {versioninfo['author']}")
    print(f"URL:       {versioninfo['url']}")
    print(f"Copyright: {versioninfo['copyright']}")
    print(f"License:   {versioninfo['license']}")
    print(f"Version:   {versioninfo['version']}")

def printdetailedversion():
    print("Builddate: {buildinfo['builddate']}")
    print("Buildhash: {buildinfo['buildhash']}")

def _scale2rows(scale):
    suffix=scale[-1].lower()
    if suffix == 'm':
        return int(scale[:-1]) * 2**20//8192
    elif suffix == 'g':
        return int(scale[:-1]) * 2**30//8192
    elif suffix == 't':
        return int(scale[:-1]) * 2**40//8192
    return int(scale) * 2**20//8192

def _rows2scale(rows):
    bytes = rows*8192
    mib = bytes/1048576
    gib = mib/1024
    tib = gib/1024
    if bytes < 2**30:
        return f'{mib:.2f}M'
    elif bytes < 2**40:
        return f'{gib:.2f}G'
    else:
        return f'{tib:.2f}T'

class Config():
    parameters = {
        'dbhost': 'localhost',
        'dbname': 'pgio',
        'dbuser': 'pgio',
        'dbpass': 'pgio',
        'dbport': None,
        'update_pct': 0,
        'rows': 131072,
        'schemas': 4,
        'work_unit': 255,
        'update_unit': 8,
        'tablespace': None
    }

    def __init__(self):
        self.info  = {}
        self.path  = os.path.join(os.path.expanduser('~'), '.config/pgio', 'pgio.json')
        self.dirty = False
        self.load()

    def __del__(self):
        if self.dirty:
            self.save()

    def __getattr__(self, name: str):
        if name == 'scale':
            return self.info['rows']
        elif name == 'size':
            return _rows2scale(self.info['rows'])
        elif name in self.parameters:
            return self.info.get(name)
        else:
            raise KeyError(f'Invalid parameter {name}')

    def set(self, name, value):
        if name == 'scale':
            self.info['rows'] = _scale2rows(value)
        elif name in self.parameters:
            self.dirty = True
            self.info[name] = value
        else:
            raise KeyError(f'Invalid parameter {name}')

    def reset(self):
        info = {k: self.parameters[k] for k in self.parameters if not k in ('dbhost','dbname','dbuser','dbpass')}
        self.info.update(info)
        self.dirty=True

    def configure(self, args):
        if args.defaults:
            self.reset()
   
        for parameter in self.parameters:
            if not parameter in args:
                continue
            val = getattr(args, parameter)
            if val is not None:
                self.dirty=True
                self.set(parameter, val)
        if args.scale:
            self.dirty=True
            self.set('scale', args.scale)

        self.show()

    def load(self):
        try:
            self.info.update(self.parameters)
            with open(self.path) as f:
                info = json.load(f)
            self.info.update(info)
        except FileNotFoundError:
            self.reset()
            self.save()
        except json.decoder.JSONDecodeError:
            os.unlink(self.path)
            raise ValueError(f'{self.path}: Bad JSON format')

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(self.info, f, indent=2, sort_keys=True)

    def show(self):
        for k, v in sorted(self.info.items()):
            if v is None:
                continue
            print(f'{k:20} {v}')
            if k == 'rows':
                sz = _rows2scale(v)
                print(f'{"schema_size":20} {sz}')
            