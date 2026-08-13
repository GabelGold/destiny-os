#!/usr/bin/env python3
import subprocess
import time

from destiny_paths import DestinyPaths


def pull_once() -> bool:
    """Pull only if this install is a git checkout. Returns True if pull ran."""
    root = DestinyPaths.root()
    if not DestinyPaths.has_git():
        print(f"Kein .git unter {root} – git pull übersprungen.")
        return False
    result = subprocess.run(
        ["git", "-C", str(root), "pull"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"git pull fehlgeschlagen: {result.stderr.strip()}")
        return False
    print(result.stdout.strip() or "git pull ok")
    return True


def main():
    while True:
        pull_once()
        time.sleep(1800)


if __name__ == "__main__":
    main()
