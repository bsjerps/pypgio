
"""
installer.py - Installs/Deinstalls the PyPGIO virtual environment
Copyright (c) 2023 - Bart Sjerps <bart@dirty-cache.com>
License: GPLv3+
"""

import os, sys, re, argparse
from subprocess import run, PIPE, CalledProcessError
from pkgutil import get_data

homedir         = os.path.expanduser('~')
venvdir         = os.path.join(homedir, 'pgio_venv')
bash_completion = os.path.join(homedir, '.bash_completion')
completions     = os.path.join(homedir, '.local/share/bash-completion/completions')
complete_pgio   = os.path.join(completions, 'complete_pgio')
configfile      = os.path.join(homedir, '.config/pgio', 'pgio.json')

required    = ('prettytable', 'psycopg', 'psycopg-binary', 'wcwidth')

def make_completions():
    os.makedirs(completions, exist_ok=True)

    if not os.path.isfile(bash_completion):
        with open(bash_completion, 'w') as f:
            pass

    with open(bash_completion) as f:
        data = f.read()
    if not re.search(r'completions/*', data):
        with open(bash_completion, 'a') as f:
            f.write("for f in $HOME/.local/share/bash-completion/completions/* ; do source $f ; done\n")

    with open(complete_pgio, 'wb') as f:
        data = get_data('lib', 'complete_pgio')
        print(f"Saving {complete_pgio}")
        f.write(data)

def make_venv():
    pip = os.path.join(venvdir, 'bin', 'pip')

    # Create venv
    if not os.path.isdir(venvdir):
        try:
            run(['python3', '-m', 'venv', venvdir], check=True)
        except CalledProcessError:
            run(['/usr/bin/rm', '-rf', venvdir])
            print(f'Creating virtual environment failed, try "sudo apt-get install python3-venv"')
            return
    try:
        run([pip, 'install', '--upgrade', 'pip'], check=True)
    except (CalledProcessError, FileNotFoundError):
        print("Install PIP packages failed")
        run(['/usr/bin/rm', '-rf', venvdir])
    
    # Install required packages
    r = run([pip, 'freeze'], stdout=PIPE, encoding='utf-8', check=True)
    installed = re.findall('(\S+)==.*', r.stdout)
    for pkg in required:
        if not pkg in installed:
            run([pip, 'install', pkg], check=True)

def install(*args, **kwargs):
    try:
        make_completions()
        make_venv()
        print("\nNow logout and login again to activate pgio bash completion\n")
        print("Or run:\n\nsource ~/.bash_completion\n")
    except (CalledProcessError, FileNotFoundError):
        print("Install failed")

def uninstall(*args, **kwargs):
    if os.path.exists(complete_pgio):
        print(f"Deleting {complete_pgio}")
        os.unlink(complete_pgio)

    if os.path.exists(configfile):
        print(f"Deleting {configfile}")
        os.unlink(configfile)
        os.rmdir(os.path.dirname(configfile))

    if os.path.isdir(venvdir):
        print(f"Deleting virtual environment {venvdir}")
        run(['/usr/bin/rm', '-rf', venvdir])

    sys.exit()

def bootstrap(err):
    parser = argparse.ArgumentParser()
    subparsers     = parser.add_subparsers(title='commands', dest='cmd')
    parser_install = subparsers.add_parser('install',   help='(Re-)Install virtual environment', add_help=False)
    parser_uninst  = subparsers.add_parser('uninstall', help='Remove virtual environment')

    parser_install.set_defaults(func=install)
    parser_uninst.set_defaults(func=uninstall)

    args = parser.parse_args()
    if args.cmd is not None:
        args.func()
    else:
        print(f'Import failed ({err}), try pgio install')