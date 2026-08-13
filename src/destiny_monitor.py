#!/usr/bin/env python3
"""
Einfaches System-Monitoring: CPU, RAM, Disk.
Schreibt Status zyklisch nach stdout (systemd-journal).
"""

import time
from datetime import datetime
import psutil


def loop():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] CPU: {cpu}% | RAM: {mem.percent}% | Disk: {disk.percent}%")
        time.sleep(4)


if __name__ == "__main__":
    loop()
