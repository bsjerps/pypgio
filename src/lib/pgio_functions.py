"""
pgio_functions.py - Helper functions for pypgio
Copyright (c) 2023 - Bart Sjerps <bart@dirty-cache.com>
License: GPLv3+
"""

import os
from pkgutil import get_data
from buildinfo import buildinfo

versioninfo = {
    'author': "Bart Sjerps <info@dirty-cache.com>",
    'copyright': "Copyright 2023, Bart Sjerps",
    'license': "GPLv3+, https://www.gnu.org/licenses/gpl-3.0.html and Apache 2.0, http://www.apache.org/licenses/LICENSE-2.0",
    'version': "1.0.1"
}

def printversion():
    print (f"Author:    {versioninfo['author']}")
    print (f"Copyright: {versioninfo['copyright']}")
    print (f"License:   {versioninfo['license']}")
    print (f"Version:   {versioninfo['version']}")

def printdetailedversion():
    print ("Builddate: {buildinfo['builddate']}")
    print ("Buildhash: {buildinfo['buildhash']}")

def install():
    homedir = os.path.expanduser('~')
    bindir = os.path.join(homedir, 'bin')
    if not os.path.isdir(bindir):
        print(f"No {bindir}, exiting")
        return
    for name in ('install_pgio', 'complete_pgio'):
        script = get_data('lib', name).decode()
        path = os.path.join(bindir, name)
        with open(path, 'w') as f:
            f.write(script)
        os.chmod(path, 0o644)
