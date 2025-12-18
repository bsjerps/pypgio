"""
install.py - Installer functions for PyPGIO
Copyright (c) 2024 - Bart Sjerps <bart@dirty-cache.com>
Based on the original PGIO by Kevin Closson - see https://github.com/therealkevinc/pgio
License: GPLv3+
"""

import os, sys, re
from pkgutil import get_data
from subprocess import run, PIPE, CalledProcessError

homedir         = os.path.expanduser('~')
venvdir         = os.path.join(homedir, '.virtualenvs/pgio_venv')
pgiobin         = os.path.join(homedir, 'bin', 'pgio')
completions     = os.path.join(homedir, '.local/share/bash-completion/completions')
complete_pgio   = os.path.join(completions, 'complete_pgio')
bash_completion = os.path.join(homedir, '.bash_completion')
pip             = os.path.join(venvdir, 'bin', 'pip')

required = ('prettytable', 'psycopg', 'psycopg-binary', 'wcwidth')

def writefile(path, src, mode, overwrite=True):
    if not overwrite and os.path.exists(path):
        print(f'{path} already exists, skipping')
        return
    print(f"Saving {path}")
    data = get_data('install', src)
    with open(path, 'wb') as f:
        f.write(data)

    os.chmod(path, mode)

def removefile(path):
    print(f"Deleting {path}")
    try:
        os.unlink(path)
    except OSError:
        pass

def make_venv():
    try:
        if not os.path.isdir(venvdir):
            print(f"Creating virtualenv on {venvdir}")
            r = run(['python3', '-m', 'venv', venvdir], check=True)

        r = run([pip, 'freeze'], stdout=PIPE, encoding='utf-8', check=True)
        installed = re.findall('(\S+)==.*', r.stdout)
        for pkg in required:
            if not pkg in installed:
                print(f'Installing {pkg}')
                run([pip, 'install', pkg], check=True)
        print(f'Virtual environment setup finished on {venvdir}\n')
        run([pip, 'list'], check=True)
    except CalledProcessError:
        run(['/usr/bin/rm', '-rf', venvdir], check=True)
        print('Creating virtual environment failed')

def remove_venv():
    print(f"Removing virtualenv on {venvdir}")
    run(['/usr/bin/rm', '-rf', venvdir], check=True)

def install():
    os.makedirs(os.path.join(homedir, 'bin'), exist_ok=True)
    os.makedirs(completions, exist_ok=True)
    writefile(pgiobin, 'pgio', 0o755)
    writefile(complete_pgio, 'complete_pgio', 0o644)
    writefile(bash_completion, 'bash_completion', 0o644, overwrite=False)
    make_venv()
    print("\nNow logout and login again to activate pgio bash completion, or run:")
    print("\nsource ~/.bash_completion\n")

def uninstall():
    remove_venv()
    removefile(pgiobin)
    removefile(complete_pgio)
