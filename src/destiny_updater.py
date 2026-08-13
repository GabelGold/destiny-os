#!/usr/bin/env python3
"""
Destiny Updater – nur explizit, kein stiller Perioden-Pull.
"""

import argparse
import subprocess
import sys

from destiny_paths import DestinyPaths


def update(force: bool = False) -> bool:
    """Führt git pull aus, wenn .git existiert."""
    root = DestinyPaths.root()
    if not DestinyPaths.has_git():
        print(f"Kein Git-Repository unter {root}")
        return False
    cmd = ["git", "-C", str(root), "pull"]
    if force:
        cmd.append("--ff-only")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except Exception as exc:
        print(f"Update fehlgeschlagen: {exc}")
        return False
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    return result.returncode == 0


def status() -> int:
    root = DestinyPaths.root()
    if not DestinyPaths.has_git():
        print(f"Kein Git-Repository unter {root}")
        return 1
    result = subprocess.run(["git", "-C", str(root), "status", "-sb"])
    return result.returncode


def pull_once() -> bool:
    """Kompatibilität: kein Loop, ein expliziter Pull."""
    return update()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Destiny Updater (explizit)")
    parser.add_argument("--update", action="store_true", help="Fuehrt git pull aus")
    parser.add_argument("--status", action="store_true", help="Zeigt Git-Status")
    parser.add_argument("--force", action="store_true", help="git pull --ff-only")
    args = parser.parse_args(argv)

    if args.update:
        return 0 if update(force=args.force) else 1
    if args.status:
        return status()
    print("Verwendung: python destiny_updater.py --update")
    print("            python destiny_updater.py --status")
    return 2


if __name__ == "__main__":
    sys.exit(main())
