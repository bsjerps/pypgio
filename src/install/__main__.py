"""
__main__.py - main python file for running installer module from PyPGIO zipapp
Copyright (c) 2024 - Bart Sjerps <bart@dirty-cache.com>
Based on the original PGIO by Kevin Closson - see https://github.com/therealkevinc/pgio
License: GPLv3+
"""

import argparse
from install import install, uninstall

help = """\
Sets up a virtual environment and installs the wrapper scripts to run pgio directly from the command line.
Also installs the bash completions file.
"""

parser = argparse.ArgumentParser(description="Installer for pypgio", epilog=help)
parser.add_argument('-u','--uninstall', action="store_true", help="Remove wrapper and completion files")
args = parser.parse_args()

if args.uninstall:
    uninstall()
else:
    install()
