#!/usr/bin/env python3.10
import re
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Change the environment file location
global ENV_FILE
ENV_FILE = Path("/home/kali/ctf/active-ips").resolve()
ENTRY_REGEX = re.compile("^export\\s+([\\w]+)=(.*)[\n\r]?$", flags=re.IGNORECASE)


@dataclass
class Entry:
    key: str
    value: str

    def __post_init__(self):
        self.key = self.key.upper()

    def __str__(self):
        return f"export {self.key.upper()}={self.value}"


def parse_args(args: list):
    def resolve_path_arg(path: str):
        return Path(path).resolve()

    parser = ArgumentParser(description="Script to manage environment variables")
    if not args:
        parser.print_usage()
        sys.exit(1)
    parser.add_argument(
        "-e",
        "--env-file",
        type=resolve_path_arg,
        default=ENV_FILE,
        help="Alternate environment file",
    )
    parse_subcommands(parser)
    return parser.parse_args(args)


def parse_subcommands(parser):
    subparsers = parser.add_subparsers(dest="action")
    parse_add(subparsers)
    parse_show(subparsers)
    parse_edit(subparsers)
    parse_delete(subparsers)


def parse_add(subparsers):
    # test = subparsers.add_parser("test")
    add = subparsers.add_parser("add")
    add.add_argument("key", help="Name of the variable")
    add.add_argument("value", help="Value of the variable")


def parse_edit(subparsers):
    edit = subparsers.add_parser("edit")
    edit.add_argument("key", help="Name of the variable")
    edit.add_argument("value", help="New value of the variable")


def parse_delete(subparsers):
    delete = subparsers.add_parser("del")
    delete.add_argument("key", nargs="+", help="Name of the variable to delete")
    delete.add_argument("-f", "--force", help="Don't prompt")


def parse_show(subparsers):
    show = subparsers.add_parser("show")
    show.add_argument(
        "pattern",
        nargs="?",
        default=".",
        help="Regex pattern or name of the variable to show",
    )
    show.add_argument("--by-value", action="store_true", help="Search entries by value")


def show_entries(pattern: str, by_value: bool = False):
    """Show all entries based on the given regex pattern.

    - Regex flag IGNORECASE is set
    - by_value=True - uses the key as the target for the pattern"""
    entries = load_entries()
    target = "value" if by_value else "key"
    for entry in entries:
        match = re.search(pattern, entry.__dict__.get(target, ""), flags=re.IGNORECASE)
        if match:
            print(entry)


def edit_entry(key: str, new_value: str):
    """Overwrite the env. file excluding with modified entry"""
    all_entries = load_entries()
    new_entry = Entry(key, new_value)
    for entry in all_entries:
        if entry.key != new_entry.key:
            continue
        entry.value = new_entry.value
        break
    else:
        return print(f"Entry with key '{new_entry.key}' does not exist.")

    write_entries(all_entries)


def delete_entries(keys: list[str]):
    """Delete multiple entries in the env. file"""
    for key in keys:
        delete_entry(key)


def delete_entry(key: str):
    """Overwrite the env. file excluding an single entry by key"""
    all_entries = load_entries()
    for i, entry in enumerate(all_entries):
        if entry.key != key.upper():
            continue
        del all_entries[i]
        break
    else:
        return print(f"Entry with key '{key.upper()}' does not exist.")

    write_entries(all_entries)


def write_entries(entries: list[Entry]) -> None:
    """Overwrite the environment variable file with new entries"""
    content = "".join([f"{e}\n" for e in entries])
    ENV_FILE.write_text(data=content, encoding="utf-8")
    print("New content:\n")
    print(ENV_FILE.read_text())


def add_entry(key: str, value: str) -> None:
    """Add a single entry to the environment variable file if it doesn't exist"""
    all_entries = load_entries()
    new_entry = Entry(key, value)
    entry_exists = bool(list(filter(lambda x: x.key == new_entry.key, all_entries)))
    if not entry_exists:
        write_entry(new_entry)
        print("New entry added!")
    else:
        print(f"Entry with key '{new_entry.key}' already exists")


def write_entry(entry: Entry) -> None:
    """Append an entry to the environment variable file"""
    with ENV_FILE.open("a") as f:
        f.write(f"{entry}\n")


def filter_none(list_: list[Any]) -> list[Any]:
    """Filter out None values from a list"""
    return list(filter(None, list_))


def read_lines(path: Path) -> list[str]:
    """Read all lines in the file and filter None"""
    content = path.read_text("utf-8").strip()
    lines = content.split("\n")
    return filter_none(lines)


def load_entries() -> list[Entry]:
    """Load all valid entries from the environment variable file"""
    lines = read_lines(ENV_FILE)
    entries = []
    for line in lines:
        if entry := parse_line(line):
            entries.append(entry)
    return entries


def parse_line(line: str) -> Entry:
    """Parse a environment variable file line into an Entry object"""
    if match := ENTRY_REGEX.search(line):
        return Entry(key=match.group(1), value=match.group(2))


def configure_env_file(env_file: Path) -> None:
    """Set a different environment variable file if different one is given"""
    global ENV_FILE
    if ENV_FILE == env_file:
        print(f"Using preconfigured ENV: {env_file}")
    else:
        ENV_FILE = env_file
        print(f"Using given ENV: {env_file}")


def main(args):
    configure_env_file(args.env_file)
    match args.action:
        case "add":
            print(f"~> Add a new entry '{args.key}' -> '{args.value}'")
            add_entry(args.key, args.value)
        case "show":
            print(f"~> Showing entries by pattern '{args.pattern}'")
            show_entries(args.pattern, args.by_value)
        case "edit":
            print(f"~> Modifying key '{args.key}' -> '{args.value}'")
            edit_entry(args.key, args.value)
        case "del":
            print(f"~> Deleting entry with key '{args.key}'")
            delete_entries(args.key)
        case _:
            print("No such action")
            sys.exit(1)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(args)
