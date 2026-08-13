#!/usr/bin/env python3
import os
import subprocess
import sys
import time
from pathlib import Path

from destiny_paths import DestinyPaths

DestinyPaths.ensure()
LOG = DestinyPaths.logs() / "commander.log"


def log(msg):
    LOG.parent.mkdir(exist_ok=True, parents=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")
    print("⚡", msg)


def _windows_actions():
    src = DestinyPaths.src()
    py = DestinyPaths.python()
    return {
        "restart gui": [py, "-m", "streamlit", "run", str(src / "destiny_gui.py")],
        "restart core": [py, str(src / "destiny_manager.py")],
        "update now": [py, str(src / "destiny_updater.py")],
        "heal": [py, str(src / "destiny_watchdog.py")],
        "backup now": [py, str(src / "destiny_backup_agent.py")],
    }


def _linux_actions():
    return {
        "restart gui": ["systemctl", "restart", "destiny_gui.service"],
        "restart core": ["systemctl", "restart", "destiny_core.service"],
        "update now": ["systemctl", "restart", "destiny_updater.service"],
        "heal": ["systemctl", "restart", "destiny_watchdog.service"],
        "backup now": ["systemctl", "restart", "destiny_backup.service"],
    }


def command_map():
    return _windows_actions() if DestinyPaths.is_windows() else _linux_actions()


def run(action):
    log(f"Running: {action}")
    if isinstance(action, (list, tuple)):
        subprocess.Popen(list(action), cwd=str(DestinyPaths.root()))
    else:
        os.system(str(action))


def main():
    log("Commander online")
    inbox = DestinyPaths.inbox()
    inbox.parent.mkdir(parents=True, exist_ok=True)
    actions = command_map()
    while True:
        if inbox.exists():
            cmd = inbox.read_text(encoding="utf-8").strip().lower()
            log(f"Received command: {cmd}")
            inbox.unlink()
            for key, action in actions.items():
                if key in cmd:
                    run(action)
                    break
            else:
                log("❓ Unknown command")
        time.sleep(2)


if __name__ == "__main__":
    main()
