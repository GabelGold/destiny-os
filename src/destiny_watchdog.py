#!/usr/bin/env python3
"""
Watchdog: restart services only after a failed health-check.
"""

import subprocess
import sys
import time

from destiny_paths import DestinyPaths

SERVICES = ["destiny_gui", "destiny_core", "destiny_monitor"]
CHECK_INTERVAL = 900


def health_check() -> bool:
    try:
        from destiny_manager import DestinyManager

        mgr = DestinyManager()
        status = mgr.health_check()
        return status.get("status") in ("healthy", "recovered")
    except Exception as exc:
        print(f"Health-Check fehlgeschlagen: {exc}")
        return False


def restart_linux():
    for svc in SERVICES:
        subprocess.run(["systemctl", "restart", f"{svc}.service", "--no-block"], check=False)


def restart_windows():
    src = DestinyPaths.src()
    py = DestinyPaths.python()
    mapping = {
        "destiny_core": [py, str(src / "destiny_manager.py")],
        "destiny_monitor": [py, str(src / "destiny_monitor.py")],
        "destiny_gui": [py, "-m", "streamlit", "run", str(src / "destiny_gui.py")],
    }
    for name, cmd in mapping.items():
        print(f"Windows-Neustart: {name}")
        subprocess.Popen(cmd, cwd=str(DestinyPaths.root()))


def restart_services():
    if DestinyPaths.is_windows():
        restart_windows()
    else:
        restart_linux()


def main():
    while True:
        if health_check():
            print("Health-Check ok – kein Restart.")
        else:
            print("Health-Check fehlgeschlagen – starte Module neu.")
            restart_services()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
