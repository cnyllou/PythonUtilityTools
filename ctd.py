"""
Script for switching to my ctf directories faster
"""
import sys
from argparse import ArgumentParser
from pathlib import Path

import pyautogui

BASE_PATH = Path("/home/kali/ctf/")


def parse_args():
    parser = ArgumentParser(description="Automation script for quick navigation")
    parser.add_argument("root")
    parser.add_argument("sub", nargs="?", default="")
    return parser.parse_args()


def make_pattern(root: str = "", sub: str = ""):
    """Create a glob pattern"""
    root_given, sub_given = bool(root), bool(sub)
    match (root_given, sub_given):
        case (True, False):
            return f"*/*{root}*"
        case (False, True):
            return f"*{sub}*/*"
        case (True, True):
            return f"*{sub}*/*{root}*"
        case _:
            return "*"


def search_path(root: str, sub: str = "") -> str:
    """Use multiple search functions to find the directory"""
    pattern = make_pattern(root, sub)
    print(f"[*] Using created pattern method first: {pattern}")
    path = recursive_glob(BASE_PATH, pattern)
    if not path:
        print("[*] Using permissive lowercase recursive glob")
        pattern = make_pattern(sub=sub)
        print(pattern)
        path = recursive_glob_lowercase_wildcard(BASE_PATH, pattern, root)
    return path


def recursive_glob(root_path, pattern) -> str:
    """Use recursive glob to find the first matching pattern"""
    for path in root_path.rglob(pattern):
        if path.is_dir():
            return str(path)
    return ""


def recursive_glob_lowercase_wildcard(root_path, pattern, to_search):
    """Use recursive glob and find the first matching directory with
    a lowercase search string"""
    for path in root_path.rglob(pattern):
        if path.is_dir() and to_search.lower() in path.name.lower():
            return path
    return ""


def main():
    path = search_path(args.root, args.sub)
    if not path:
        sys.exit(f"Did not find such root {args.root}, in directory: {args.sub}")
    print("Found:", path)
    pyautogui.write(path)
    pyautogui.press(["enter"])


if __name__ == "__main__":
    args = parse_args()
    main()
