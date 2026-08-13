#!/usr/bin/env python3
"""
Destiny Power Center – startet Module auf Linux (systemd) und Windows (Prozess).
"""

import subprocess
import sys

from destiny_paths import DestinyPaths


class DestinyPowerCenter:
    def __init__(self):
        self.modules = {
            "Self-Healing AI": self.enable_self_healing,
            "Auto-Backup Engine": self.enable_auto_backup,
            "Voice Commander": self.enable_voice,
            "Live Monitoring": self.enable_monitor,
        }

    def list_modules(self):
        return list(self.modules.keys())

    def _linux_service(self, unit: str):
        subprocess.run(["sudo", "systemctl", "enable", unit], check=False)
        subprocess.run(["sudo", "systemctl", "start", unit], check=False)

    def _windows_start(self, label: str, args: list[str]):
        print(f"Windows: starte {label}")
        subprocess.Popen(args, cwd=str(DestinyPaths.root()))

    def enable_self_healing(self):
        if DestinyPaths.is_windows():
            self._windows_start(
                "Watchdog",
                [DestinyPaths.python(), str(DestinyPaths.src() / "destiny_watchdog.py")],
            )
            print("Self-Healing auf Windows: Watchdog-Prozess gestartet (kein permanenter Task).")
        else:
            self._linux_service("destiny_watchdog.service")
            print("Self-Healing-Service angestossen.")

    def enable_auto_backup(self):
        if DestinyPaths.is_windows():
            self._windows_start(
                "Backup",
                [DestinyPaths.python(), str(DestinyPaths.src() / "destiny_backup_agent.py")],
            )
        else:
            self._linux_service("destiny_backup.service")
        print("Auto-Backup aktiviert.")

    def enable_voice(self):
        if DestinyPaths.is_windows():
            self._windows_start(
                "Voice",
                [DestinyPaths.python(), str(DestinyPaths.src() / "voice_commander.py")],
            )
        else:
            self._linux_service("destiny_voice.service")
        print("Voice Commander aktiviert.")

    def enable_monitor(self):
        if DestinyPaths.is_windows():
            self._windows_start(
                "Monitor",
                [DestinyPaths.python(), str(DestinyPaths.src() / "destiny_monitor.py")],
            )
        else:
            self._linux_service("destiny_monitor.service")
        print("Monitoring aktiviert.")

    def activate(self, name: str):
        fn = self.modules.get(name)
        if not fn:
            print(f"Unbekanntes Modul: {name}")
            return
        fn()
