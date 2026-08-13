#!/usr/bin/env python3
"""
Sehr einfacher Backup-Agent:
Aktuell nur Platzhalter-Logik – später kannst du echte Backup-Ziele eintragen.
"""

from pathlib import Path
from datetime import datetime
import shutil
import time

SRC = Path.home() / "destiny_archive"
DST_BASE = Path.home() / "destiny_backups"
DST_BASE.mkdir(parents=True, exist_ok=True)


def run():
    while True:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
        dst = DST_BASE / f"backup_{ts}"
        if SRC.exists():
            try:
                shutil.copytree(SRC, dst)
                print(f"💾 Backup erstellt: {dst}")
            except Exception as e:
                print(f"⚠ Backup-Fehler: {e}")
        else:
            print("⚠ Kein destiny_archive gefunden, überspringe.")
        time.sleep(60 * 30)


if __name__ == "__main__":
    run()
