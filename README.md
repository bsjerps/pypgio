PyPGIO - An IO generator for PostgreSQL based on the original pgio and SLOB

# Description

__PyPGIO__ is a Python based I/O generator for PostgreSQL databases.
The only purpose is to drive (a lot of) I/O from a Postgres database without requiring a lot of CPU resources.

It is based on, and uses some code from PGIO by Kevin Closson, see [PGIO](https://github.com/therealkevinc/pgio) for more details.

# Prerequisites

* Linux shell account (can be different system than the database server)
* ```$HOME/bin``` directory that is in ```$PATH```
* PostgreSQL database (any recent supported version)
* User on the database with full access rights on the database
* Python 3.6 or higher
* ```python3``` must be in the environment
* Internet access to install Python PIP packages

# Installing

## Easy way

Assuming the prerequisites are met, the easiest way to install the latest version of _PyPGIO_ is to run the downloader command on your host:

```
# Test if python3 works
python3 --version

# This requires internet access via https
# Inspect downloader (optional)
curl https://raw.githubusercontent.com/bsjerps/pypgio/master/scripts/download | less

# Download using downloader
curl https://raw.githubusercontent.com/bsjerps/pypgio/master/scripts/download | bash

# Check if pypgio is installed
ls -al ~/bin/pypgio
```

## From GIT repo

Note that _PyPGIO_ is designed to run as a [ZipApp](https://docs.python.org/3/library/zipapp.html) package. Running directly from the git repository is not recommended. Instead, create the package from the repo:

```
# Clone the repository
git clone https://github.com/bsjerps/pypgio.git
cd pypgio
scripts/mkapp
ls -al ~/bin/pypgio
```

# Setup the environment

_PyPGIO_ depends on the Python modules [psycopg](https://www.psycopg.org/) and [PrettyTable](https://pypi.org/project/prettytable/). These modules are not installed by default with Python. In order for _PyPGIO_ to work, it needs to run from a Python virtual environment in which these modules are installed.

To make life easier if you are not familiar with Python, _PyPGIO_ has a built-in installer module to setup the environment automatically. The virtual environment will be in ```$HOME/pgio_venv```

```
# Show the installer help
python3 $HOME/bin/pypgio/install -h

# Setup virtualenv, pgio wrapper script and bash completions
python3 $HOME/bin/pypgio/install -h

# Uninstall virtualenv, wrapper script and completions file
python3 $HOME/bin/pypgio/install -u

# Logout and login again - bash completion should now work
# Or source the completions
source ~/.bash_completion
```

# Create database
See [create_db.sql](https://github.com/bsjerps/pypgio/blob/devel/scripts/create_db.sql) for details

# Setup the environment


```
# Run pgio
pgio

# Show help summary: Run pgio -h
pgio -h

# Show default configuration settings
pgio configure

# Show configuration parameters
pgio configure -h

# Change the database host
pgio configure --dbhost pgserver.lan

# Test connection
pgio

```

# Usage

Assuming we have a database named _pgio_ with a user _pgio_ and password _pgio_.
By default, pgio uses the public table with the default schema. 

On RHEL, the database top directory is ```/var/lib/pgsql/<version>/data```

But in many cases, we want the (large) pgio tables on another filesystem. In our example we have a file system ```/pgdata``` on which we created a PostgreSQL tablespace ```bulk``` and we want our tables to be generated there.

```
# Set schemas and scale
pgio configure --schemas 8 --scale 256M

# Optionally set the default tablespace
pgio configure --tablespace bulk

# Create database structure and tables, using 4 parallel threads
pgio setup 4

# Check the tables
pgio list
```

Now we can run _pgio_:

```
# Run pgio for 60 seconds with 8 threads
pgio run 60 8

# Change the update percentage
pgio configure --update_pct 10

# Run pgio for 60 seconds with 4 threads
pgio run 60 4


# View detailed reports
pgio report -v

```


# Deinstall

Deinstallation involves the removal of all pypgio related stuff in the database, and the virtual environment and shell settings in the user home directory

```
# Delete the database structures
pgio destroy

# Remove bash setup and virtual environment
python3 $HOME/bin/pypgio/install -u

# Remove pypgio from $HOME/bin
rm ~/bin/pypgio

```


