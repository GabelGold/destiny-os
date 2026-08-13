#!/usr/bin/env python3
"""
Destiny Manager
- zentrale Instanz
- orchestriert Provisioner, Archiver, Backup, Monitoring
- wird von GUI und Services angesprochen
"""

from datetime import datetime
import json
import time

from destiny_paths import DestinyPaths
from destiny_provisioner import DestinyProvisioner
from destiny_archiver import DestinyChatSorterPro


BASE_DIR = DestinyPaths.src()


class DestinyManager:

    def __init__(self):
        self.state_file = DestinyPaths.state_file()
        self.last_status = {}

        # Module initialisieren
        self.provisioner = DestinyProvisioner()
        self.archiver = DestinyChatSorterPro()

    # --------------------------------------------
    # SYSTEM START
    # --------------------------------------------
    def initialize(self):
        """
        Wird beim GUI Start oder beim Service Start aufgerufen
        und bereitet das System vor.
        """
        self._log("System boot request received")

        prov = self.provisioner.run()

        self.last_status = {
            "time": datetime.utcnow().isoformat(),
            "system": "initialized",
            "provision_log": prov
        }

        self._write_state(self.last_status)

        return self.last_status

    # --------------------------------------------
    # LOGGING
    # --------------------------------------------
    def _log(self, msg):
        print(f"[Manager] {msg}")

    # --------------------------------------------
    # STATUS & STATE FILES
    # --------------------------------------------
    def _write_state(self, state):
        try:
            self.state_file.parent.mkdir(exist_ok=True, parents=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self._log(f"State write error: {e}")

    # --------------------------------------------
    # CHAT ARCHIVIERUNG
    # --------------------------------------------
    def archive_chat(self, text):
        """
        GUI sendet Chat hierher
        """
        return self.archiver.store_chat(text)

    # --------------------------------------------
    # STATUS ABFRAGEN
    # --------------------------------------------
    def get_status(self):
        return self.last_status
    # --------------------------------------------
    # SELF HEALING ENGINE
    # --------------------------------------------
    def health_check(self):
        """
        Prüft Destiny Modules & repariert sie automatisch.
        """
        issues = []

        # Prüfe Provisioner
        try:
            status = self.provisioner.validate()
            if not status:
                issues.append("Provisioner Fehler → Neustart")
                self.provisioner.run()
        except:
            issues.append("Provisioner nicht erreichbar")
            self.provisioner.run()

        # Prüfe Archiver
        try:
            ok = self.archiver.ping()
            if not ok:
                issues.append("Archiver inkonsistent → Self Repair")
                self.archiver.repair()
        except:
            issues.append("Archiver Fehler → Neuinitialisieren")
            self.archiver.repair()

        # Ergebnis schreiben
        result = {
            "time": datetime.utcnow().isoformat(),
            "issues": issues,
            "status": "healthy" if not issues else "recovered"
        }

        self._write_state(result)

        return result


if __name__ == "__main__":
    DestinyPaths.ensure()
    mgr = DestinyManager()
    print(mgr.initialize())
    while True:
        print(mgr.health_check())
        time.sleep(30)
