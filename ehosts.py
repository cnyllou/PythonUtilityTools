#!/usr/bin/env python3.10
import os
import sys
from argparse import ArgumentParser

import python_hosts

HOSTS = python_hosts.Hosts()


def validate_conditions():
    if len(sys.argv) < 2:
        sys.exit("Not enough args")
    if args.action != "show" and os.getuid() != 0:
        sys.exit("Script must have root permissions")


def parser_args():
    parser = ArgumentParser(description="Tool for managing the hosts file")
    subprasers = parser.add_subparsers(dest="action")

    add = subprasers.add_parser("add", help="Add a new entry")
    add.add_argument("-t", "--type", choices=["ipv4", "ipv6"], default="ipv4")
    add.add_argument(
        "-a",
        "--append",
        action="store_true",
        help="Append to existing entry",
        default=False,
    )
    add.add_argument("ip", help="IP address")
    add.add_argument("names", nargs="+", help="New domain names to add")

    subprasers.add_parser("show", help="Show the contents")

    edit = subprasers.add_parser("edit", help="Edit existing entry")
    edit.add_argument("ip", help="IP address")
    edit.add_argument("names", nargs="+", help="New list of domain names")
    edit.add_argument(
        "-c",
        "--clear",
        action="store_true",
        default=False,
        help="Clear value before editing",
    )
    delete = subprasers.add_parser("delete", help="Delete existing entry")
    delete.add_argument(
        "-n",
        "--name",
        help="Delete matching name",
    )
    delete.add_argument(
        "-i", "--inclusive", action="store_true", default=False, help="Inclusive search"
    )
    delete.add_argument(
        "-f",
        "--force-delete",
        action="store_true",
        default=False,
        help="Delete the whole entry if no names are left",
    )
    delete.add_argument("ip", help="IP address")
    return parser.parse_args()


def print_hosts(entries: list[python_hosts.HostsEntry]):
    for entry in [x for x in entries if x.address]:
        address = str(entry.address)
        print(f"{address:<35}, {entry.names}")


def add_action(type: str, ip: str, names: list[str], append: bool = False):
    if HOSTS.exists(ip) and not append:
        sys.exit("Entry already exists!")

    entry = python_hosts.HostsEntry(entry_type=type, address=ip, names=names)
    if append:
        matching = HOSTS.find_all_matching(ip)
        if not matching:
            sys.exit("No matching entries")

        entry = matching[0]
        for name in names:
            if name in entry.names:
                sys.exit(f"'{names}' already in values")
        else:
            entry.names += names
            HOSTS.remove_all_matching(ip)

    HOSTS.add([entry])
    print(f"New entry: {entry}")
    HOSTS.write()


def show_action():
    print("".center(50, "-"))
    print_hosts(HOSTS.entries)
    print("".center(70, "-"))


def edit_action(ip: str, names: str):
    matching = HOSTS.find_all_matching(ip)
    if not matching:
        sys.exit("No matching entries")

    entry = matching[0]
    names_before = entry.names
    entry.names = names
    HOSTS.remove_all_matching(ip)
    HOSTS.add(entry)
    print(f"Edited: '{names_before}' -> '{names}'")
    HOSTS.write()


def is_exact_match(a, b):
    return a == b


def is_partial_match(a, b):
    return a in b


def delete_action(
    ip: str, pattern: str = None, inclusive: bool = False, force_delete: bool = False
):
    if not HOSTS.exists(ip):
        sys.exit(f"{ip}: Host doesn't exist")

    if pattern:
        entry = HOSTS.find_all_matching(ip)[0]
        names_before = entry.names.copy()

        is_match = is_exact_match if not inclusive else is_partial_match
        for name in list(entry.names):
            if is_match(pattern, name):
                entry.names.remove(name)

        if names_before == entry.names:
            sys.exit(f"No matches for '{pattern}'")

        if not entry.names and not force_delete:
            sys.exit("All names removed, exiting. Use `-f` to force such deletion")

        deleted_names = set(names_before) - set(entry.names)
        HOSTS.remove_all_matching(ip)
        if entry.names:
            HOSTS.add([entry])
        print(f"Deleted {deleted_names}. New {entry.names}")
    else:
        HOSTS.remove_all_matching(ip)
        print(f"Removed entry: {ip}")
    HOSTS.write()


def main() -> int:
    print(args)
    try:
        ip = args.ip
        names = args.names
        type = args.type
    except AttributeError:
        ...

    match args.action:
        case "add":
            add_action(type, ip, names, append=args.append)
        case "show":
            show_action()
        case "edit":
            edit_action(ip)
        case "delete":
            delete_action(ip, args.name, args.inclusive, args.force_delete)

    return 0


if __name__ == "__main__":
    args = parser_args()
    validate_conditions()
    sys.exit(main())
