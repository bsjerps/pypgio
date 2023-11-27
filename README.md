PyPGIO - An IO generator for PostgreSQL based on the original pgio and SLOB

# Description

__PyPGIO__ is a Python based I/O generator for PostgreSQL databases.
The only purpose is to drive (a lot of) I/O from a database without requiring a lot of CPU resources.

It is based on, and uses some code from PGIO by Kevin Closson, see [PGIO](https://github.com/therealkevinc/pgio) for more details.

# Prerequisites

* Linux shell account (can be different system than the database server)
* PostgreSQL database
* User on the database with full access rights on the database
* Python 3.6 or higher
* _python3_ must be in the environment
* Internet access to install Python PIP packages

# Installing

## Easy way

Assuming the prerequisites are met, the easiest way to install the latest version of _pypgio_ is to run the downloader command on your host:

```
# Test if python3 works
python3 --version

# This requires internet access via https
# Inspect downloader (optional)
curl https://raw.githubusercontent.com/bsjerps/pypgio/master/scripts/download | less

# Download using downloader
curl https://raw.githubusercontent.com/bsjerps/pypgio/master/scripts/download | bash

# Check if pgio is installed
ls -al ~/bin/pgio
-rwxr-xr-x 1 bart bart 42437 Nov 27 14:24 /home/bart/bin/pgio
```

## From GIT repo
```
# Clone the repository
git clone https://github.com/bsjerps/pypgio.git
cd pypgio
scripts/mkapp
ls -al ~/bin/pgio

```

# Setup the environment

```
# Run pgio - it will create an installer script named install_pgio in $HOME/bin
pgio

# Run installer
bash install_pgio

# Logout and login again - bash completion should now work
# Run pgio -h
pgio -h

# Show default configuration settings
pgio configure

# Show configuration parameters
pgio configure -h

# Change the database host
pgio configure --dbhost gp01.lan

# Test connection
pgio

```

# Usage

Assuming we have a database named _pgio_ with a user _pgio_ and password _pgio_.
By default, pgio uses the public table with the default schema. 

On RHEL, the database top directory is ```/var/lib/pgsql/16/data```

But in many cases, we want the (large) pgio tables on another filesystem. In our example we have a file system ```/pgdata``` on which we created a PostgreSQL tablespace ```bulk``` and we want our tables to be generated there.

```
# Set schemas and scale
pgio configure --schemas 8 --scale 256M

# Optionally set the default tablespace
pgio configure --tablespace bulk

# Create database structure and tables, using 4 threads
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


```
# Delete the database structures
pgio destroy 

# Simply remove the _pgio_ files from $HOME/bin:
rm -f $HOME/bin/{pgio,complete_pgio,install_pgio}

# Remove the virtual environment
rm -rf $HOME/pgio_venv

# Remove the environment settings from $HOME/.bashrc
```


