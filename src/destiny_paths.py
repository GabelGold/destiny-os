#!/usr/bin/env python3
"""
Portable path and platform helpers for Destiny OS.
No hardcoded /home or /media paths. Works on Windows (I:) and Linux.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


class DestinyPaths:
    @staticmethod
    def root() -> Path:
        return Path(__file__).resolve().parent.parent

    @staticmethod
    def src() -> Path:
        return Path(__file__).resolve().parent

    @staticmethod
    def logs() -> Path:
        return DestinyPaths.root() / "logs"

    @staticmethod
    def archive() -> Path:
        return Path.home() / "destiny_archive"

    @staticmethod
    def backup() -> Path:
        return Path.home() / "destiny_backups"

    @staticmethod
    def runtime() -> Path:
        return DestinyPaths.root() / "runtime"

    @staticmethod
    def memory() -> Path:
        return DestinyPaths.src() / "destiny_memory.sqlite"

    @staticmethod
    def state_dir() -> Path:
        return DestinyPaths.src() / "memory"

    @staticmethod
    def state_file() -> Path:
        return DestinyPaths.state_dir() / "system_state.json"

    @staticmethod
    def inbox() -> Path:
        return DestinyPaths.runtime() / "commander_in.txt"

    @staticmethod
    def incoming() -> Path:
        return DestinyPaths.archive() / "incoming"

    @staticmethod
    def pid_dir() -> Path:
        return DestinyPaths.runtime() / "services"

    @staticmethod
    def commander_port() -> int:
        return 8765

    @staticmethod
    def python() -> str:
        return sys.executable

    @staticmethod
    def is_windows() -> bool:
        return sys.platform == "win32"

    @staticmethod
    def is_linux() -> bool:
        return sys.platform.startswith("linux")

    @staticmethod
    def disk_root() -> str:
        """Filesystem root for disk_usage: current drive on Windows, '/' on Unix."""
        if DestinyPaths.is_windows():
            drive = Path.cwd().drive or DestinyPaths.root().drive or "C:"
            return drive + "\\"
        return "/"

    @staticmethod
    def has_git() -> bool:
        return (DestinyPaths.root() / ".git").is_dir()

    @staticmethod
    def ensure() -> None:
        for path in (
            DestinyPaths.logs(),
            DestinyPaths.runtime(),
            DestinyPaths.archive(),
            DestinyPaths.backup(),
            DestinyPaths.state_dir(),
            DestinyPaths.incoming(),
            DestinyPaths.pid_dir(),
        ):
            path.mkdir(parents=True, exist_ok=True)


def root() -> Path:
    return DestinyPaths.root()


if __name__ == "__main__":
    DestinyPaths.ensure()
    print(f"root     = {DestinyPaths.root()}")
    print(f"src      = {DestinyPaths.src()}")
    print(f"logs     = {DestinyPaths.logs()}")
    print(f"archive  = {DestinyPaths.archive()}")
    print(f"backup   = {DestinyPaths.backup()}")
    print(f"runtime  = {DestinyPaths.runtime()}")
    print(f"memory   = {DestinyPaths.memory()}")
    print(f"windows  = {DestinyPaths.is_windows()}")
    print(f"linux    = {DestinyPaths.is_linux()}")
    print(f"disk     = {DestinyPaths.disk_root()}")
    print(f"python   = {DestinyPaths.python()}")
    print(f"git      = {DestinyPaths.has_git()}")
