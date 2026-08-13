#!/usr/bin/env python3
"""
Backup-Agent mit Rotation (max. 5 Kopien von destiny_archive).
"""

import os
import shutil
import time
from datetime import datetime
from pathlib import Path

from destiny_paths import DestinyPaths

SRC = DestinyPaths.archive()
DST_BASE = DestinyPaths.backup()
MAX_BACKUPS = 5


def rotate_backups(backup_dir, max_backups=5):
    """Delete oldest backup_* directories until at most max_backups remain."""
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backups = [p for p in backup_dir.glob("backup_*") if p.is_dir()]
    backups.sort(key=os.path.getmtime)
    while len(backups) > max_backups:
        oldest = backups.pop(0)
        shutil.rmtree(oldest, ignore_errors=True)
        print(f"Altes Backup geloescht: {oldest}")


def run_once() -> Path | None:
    DST_BASE.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    dst = DST_BASE / f"backup_{ts}"
    if not SRC.exists():
        print("Kein destiny_archive gefunden, ueberspringe.")
        rotate_backups(DST_BASE, MAX_BACKUPS)
        return None
    try:
        shutil.copytree(SRC, dst)
        print(f"Backup erstellt: {dst}")
    except Exception as e:
        print(f"Backup-Fehler: {e}")
        dst = None
    rotate_backups(DST_BASE, MAX_BACKUPS)
    return dst


def run():
    while True:
        run_once()
        time.sleep(60 * 30)


if __name__ == "__main__":
    run()
