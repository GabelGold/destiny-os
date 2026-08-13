#!/usr/bin/env python3
"""
Einfaches System-Monitoring: CPU, RAM, Disk.
Schreibt Status zyklisch nach stdout (systemd-journal / Konsole).
"""

import time
from datetime import datetime

import psutil

from destiny_paths import DestinyPaths

DestinyPaths.ensure()
MONITOR_LOG = DestinyPaths.logs() / "monitor.log"


def disk_target() -> str:
    return DestinyPaths.disk_root()


def sample() -> str:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(disk_target())
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{ts}] CPU: {cpu}% | RAM: {mem.percent}% | Disk: {disk.percent}% ({disk_target()})"


def loop():
    MONITOR_LOG.parent.mkdir(parents=True, exist_ok=True)
    while True:
        line = sample()
        print(line)
        with MONITOR_LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        time.sleep(4)


if __name__ == "__main__":
    loop()
