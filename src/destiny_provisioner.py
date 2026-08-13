#!/usr/bin/env python3
"""
Destiny Provisioner
- sorgt dafür, dass beim Systemstart alles vorhanden ist
- erstellt fehlende Ordner / Dateien
- meldet Status an DestinyManager zurück
"""

import os
from pathlib import Path
import json
from datetime import datetime

from destiny_paths import DestinyPaths


BASE_DIR = DestinyPaths.src()
LOG_FILE = DestinyPaths.logs() / "system_provision_log.json"


class DestinyProvisioner:

    def __init__(self):
        self.events = []
        self.required_paths = [
            DestinyPaths.logs(),
            DestinyPaths.state_dir(),
            DestinyPaths.backup(),
            DestinyPaths.runtime(),
            DestinyPaths.archive(),
        ]
        self.required_files = [
            DestinyPaths.state_file(),
        ]

    # ---------- Logging ----------
    def _log(self, msg: str):
        event = {
            "time": datetime.utcnow().isoformat(),
            "msg": msg
        }
        self.events.append(event)

    # ---------- Run ----------
    def run(self):
        self._log("Provisioner gestartet")

        self._ensure_dirs()
        self._ensure_files()

        self._log("Provisioner abgeschlossen")
        self._write_log()

        return {
            "status": "ok",
            "detail": f"{len(self.events)} Tasks ausgeführt",
            "log": self.events
        }

    # ---------- Ensure Directory Structure ----------
    def _ensure_dirs(self):
        for p in self.required_paths:
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
                self._log(f"Ordner erstellt: {p}")
            else:
                self._log(f"Ordner vorhanden: {p}")

    # ---------- Ensure Default Files ----------
    def _ensure_files(self):
        for f in self.required_files:
            if not f.exists():
                try:
                    f.parent.mkdir(exist_ok=True, parents=True)
                    with open(f, "w", encoding="utf-8") as w:
                        json.dump({"initialized": True}, w, indent=2)
                    self._log(f"Systemdatei erzeugt: {f}")
                except Exception as e:
                    self._log(f"Fehler beim Erstellen von {f}: {e}")
            else:
                self._log(f"Systemdatei vorhanden: {f}")

    # ---------- Write Provision Log ----------
    def _write_log(self):
        try:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.events, f, indent=2)
        except Exception:
            pass
    def validate(self):
        """Fake-Check bis echte Checks dazukommen."""
        return True

    def ping(self):
        return True

    def repair(self):
        return self.run()
