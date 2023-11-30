
"""
installer.py - Installs/Deinstalls the PyPGIO virtual environment
Copyright (c) 2023 - Bart Sjerps <bart@dirty-cache.com>
License: GPLv3+
"""

import os, re, argparse
from subprocess import run, PIPE, CalledProcessError
from pkgutil import get_data

homedir     = os.path.expanduser('~')
venvdir     = os.path.join(homedir, 'pgio_venv')
completions = os.path.join(homedir, '.bash_completion')
completedir = os.path.join(homedir, '.local/share/bash-completion/completions')
complete    = os.path.join(completedir, 'complete_pgio')

required    = ('prettytable', 'psycopg', 'psycopg-binary', 'wcwidth')

def makefiles():
    os.makedirs(completedir, exist_ok=True)
    for name in ('.bash_completion', '.bash_aliases'):
        path = os.path.join(homedir, name)
        if not os.path.isfile(path):
            with open(path, 'w') as f:
                pass

    with open(complete, 'wb') as f:
        data = get_data('lib', 'complete_pgio')
        print(f"Saving {complete}")
        f.write(data)

    with open(completions) as f:
        data = f.read()
    if not re.search(r'pgio', data):
        with open(completions, 'a') as f:
            f.write(f"source {complete}\n")

def virtualenv():
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
        makefiles()
        virtualenv()
        print("Now logout and login again to activate pgio bash completion")
    except (CalledProcessError, FileNotFoundError):
        print("Install failed")

def uninstall(*args, **kwargs):
    if os.path.exists(complete):
        print(f"Deleting {complete}")
        os.unlink(complete)

    if os.path.exists(completions):
        with open(completions) as f:
            data = f.read()
        if re.search(r'pgio', data):
            out = re.sub('^source .*complete_pgio\n','', data, re.M)
            with open(completions, 'w') as f:
                f.write(out)
    
    if os.path.isdir(venvdir):
        run(['/usr/bin/rm', '-rf', venvdir])

def bootstrap():
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
        print('Missing environment, try pgio install')