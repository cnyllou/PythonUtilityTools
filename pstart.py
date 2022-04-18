"""Workflow Orchestrator

Program for orchestrating what commands will be run in what profile. The
configuration is done by using a config file (by default `pstart.config.yaml`
in module directory), which can be changed to a different path, but through
the source code."""
import functools
import os
import shlex
import subprocess
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar

import yaml

DESCRIPTION = (
    "Workflow Orchestrator, run commands based on the "
    "configured profile in the configuration file"
)

MODULE_DIR = Path(__file__).parent
CONFIG_PATH = MODULE_DIR / "pstart.config.yaml"

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_path(x: Any) -> Path | None:
    return Path(x) if x else None


def from_list(f: Callable[[Any], T], x: Any) -> list[T]:
    assert isinstance(x, list)
    return list(map(f, x))


@dataclass
class LaunchOpts:
    name: str
    opts: str = ""
    path: Path = None
    command: str = ""

    @classmethod
    def from_dict(cls, obj) -> "LaunchOpts":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name", ""))
        opts = from_str(obj.get("opts", ""))
        path = from_path(obj.get("path"))
        return cls(name, opts, path)


@dataclass
class Config:
    run_map: dict[str, str]
    paths: list[Path]
    profiles: dict[str, list[LaunchOpts]]

    @classmethod
    def from_dict(cls, obj) -> "Config":
        assert isinstance(obj, dict)
        run_map = obj.get("run_map", {})
        paths = from_list(from_path, obj.get("paths", []))
        profiles = obj.get("profiles", {})
        for name, launch_opts in profiles.items():
            profiles[name] = from_list(LaunchOpts.from_dict, launch_opts)

        return cls(run_map, paths, profiles)


def load_config() -> Config:
    return Config.from_dict(yaml.safe_load(CONFIG_PATH.open("r")))


def global_config(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = load_config()
        return func(config, *args, *kwargs)

    return wrapper


def parse_args():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "profile", nargs="?", help="Configured profile to run", default="all"
    )
    return parser.parse_args()


def which(program: str, search_paths: str = os.environ["PATH"]):
    def is_exe(fpath: str):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath and is_exe(program):
        return program
    else:
        for path in search_paths.split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def find_executable(name: str, paths: list[Path]):
    """Find executable by name, first in given paths and then only in system
    paths, returns the full path string or None

    Disclaimer:
        Looking through the PATH variable might be insecure in case the SUID/GUID
        bit is set, make sure to hard-code or remove the `or which(name)` if you're
        planning to set the bits"""
    paths = ":".join(list(map(str, paths)))
    return which(name, paths) or which(name)


@global_config
def run_launch_opts(cfg: Config, launch_opts: LaunchOpts, search_paths: list[Path]):
    """Run each launch configuration and search for the program if path not given"""
    for opts in launch_opts:
        cmd = cfg.run_map.get(opts.name)
        full_path = cmd or opts.path or find_executable(opts.name, search_paths)
        if not full_path:
            print(f"Failed to find '{opts.name}'")
            continue

        cmd = cmd or f"{full_path} {opts.opts}"
        print(f"> {cmd}")
        ret = subprocess.call(shlex.split(cmd), stderr=subprocess.DEVNULL)
        if ret == 1:
            print(f"Command: `{cmd}` failed!")


@global_config
def main(cfg: Config):
    launch_opts = cfg.profiles[args.profile]
    run_launch_opts(launch_opts, cfg.paths)


if __name__ == "__main__":
    args = parse_args()
    main()
