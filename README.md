# PythonUtilityTools

Set of my utility tools I use.

## Setup

Most of the tool setup will be done by installing the requirements.

- Should have at least Python 3.10

```bash
# (optional) python -m venv venv; . venv/bin/activate
$ pip install -r requirements.txt
```

## `env-man.py` - Environment Variable Manager

I can add, edit, delete, and show all variables by regex pattern.

I use this when doing CTFs and doing TryHackMe rooms so it's easier to set the IP
variable or other shortcuts for cases when the IP won't be the same.

### Prerequisites

Create a new file for only environment variables.

Add `source /path/to/env-file` to your `~/.bashrc` file (or `~/.zshrc`).

### IMPORTANT

Change `ENV_FILE` to point at yours, the environment variable file **MUST contain only environment variables**,
otherwise an edit or delete **WILL OVERWRITE everything**.

## `pstart.py` - Workflow Orchestrator

Program for orchestrating what commands will be run in what profile. The
configuration is done by using a YAML configuration file (by default
`pstart.config.yaml` in module directory), which can be changed to a different
path, but through the source code.


## `ctd.py` - Change (to CTF) directory

Personal script for quickly navigating to one of my CTF directories
