"""
pgio_functions.py - Helper functions for pypgio
Copyright (c) 2023 - Bart Sjerps <bart@dirty-cache.com>
License: GPLv3+
"""

import os
from pkgutil import get_data
from buildinfo import buildinfo

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
