# PythonUtilityTools

Set of my utility tools I use.

## env-man

Environment variable manager, I can add, edit, delete, and show all variables by regex pattern.

I use this when doing CTFs and doing TryHackMe rooms so it's easier to set the IP variable or other
shortcuts for cases when the IP won't be the same.

### Prequisites

Create a new file for only environment variables.

Add `source /path/to/env-file` to your `~/.bashrc` file (or `~/.zshrc`).

### IMPORTANT

Change `ENV_FILE` to point at yours, the environment variable file **MUST contain only environment variables**,
otherwise an edit or delete **WILL OVERWRITE everything**.

## ctd

Personal script for quickly navigating to one of my ctf directories
