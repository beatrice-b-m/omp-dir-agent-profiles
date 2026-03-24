from __future__ import annotations

import argparse
import sys

from dir_agent_profile.profiles import load_profiles, remove_profile
from dir_agent_profile.config import apply_profile
from dir_agent_profile.interactive import run_interactive


def _cmd_list() -> None:
    profiles = load_profiles()
    if not profiles:
        print("No saved profiles.")
        return
    for name, roles in profiles.items():
        print(f"{name}:")
        for role, model in roles.items():
            print(f"  {role}: {model}")


def _cmd_apply(name: str) -> None:
    profiles = load_profiles()
    profile = profiles.get(name)
    if profile is None:
        print(f"Error: Profile '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    apply_profile(profile)
    print(f"Profile '{name}' applied to current directory.")


def _cmd_remove(name: str) -> None:
    existed = remove_profile(name)
    if not existed:
        print(f"Error: Profile '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    print(f"Profile '{name}' removed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage OMP model role profiles")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", metavar="NAME", help="Apply a named profile")
    group.add_argument("--list", action="store_true", help="List all saved profiles")
    group.add_argument("--remove", metavar="NAME", help="Remove a named profile")

    args = parser.parse_args()

    if args.list:
        _cmd_list()
    elif args.apply is not None:
        _cmd_apply(args.apply)
    elif args.remove is not None:
        _cmd_remove(args.remove)
    else:
        run_interactive()
