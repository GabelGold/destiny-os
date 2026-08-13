#!/usr/bin/env python3
"""
Destiny Power Center – Module starten und optional persistieren
(Windows: Task Scheduler / NSSM, Linux: systemd).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from destiny_paths import DestinyPaths
from destiny_service_manager import DestinyServiceManager


class DestinyPowerCenter:
    def __init__(self):
        self.svc = DestinyServiceManager()
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

    def enable_windows_persistence(self, service_name: str, script_path=None) -> bool:
        """Registriert einen Task, der beim Systemstart läuft."""
        info = self.svc.services.get(service_name)
        if not info:
            print(f"Unbekannter Service: {service_name}")
            return False
        cmd = self.svc.command_for(service_name)
        quoted = " ".join(f'"{part}"' if " " in part else part for part in cmd)
        task_name = f"Destiny_{service_name}"
        create = [
            "schtasks",
            "/Create",
            "/TN",
            task_name,
            "/TR",
            quoted,
            "/SC",
            "ONSTART",
            "/RL",
            "LIMITED",
            "/F",
        ]
        result = subprocess.run(create, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Task {task_name} erstellt")
            return True
        print(f"Task {task_name} fehlgeschlagen: {result.stderr.strip() or result.stdout.strip()}")
        return False

    def enable_nssm_service(self, service_name: str, script_path=None) -> bool:
        """NSSM-Service, sonst Task Scheduler."""
        nssm = shutil.which("nssm")
        if not nssm:
            print("NSSM nicht installiert – Fallback Task Scheduler")
            return self.enable_windows_persistence(service_name, script_path)
        info = self.svc.services.get(service_name)
        if not info:
            return False
        cmd = self.svc.command_for(service_name)
        display = f"Destiny_{service_name}"
        install = [nssm, "install", display, cmd[0]]
        if len(cmd) > 1:
            install.extend(cmd[1:])
        result = subprocess.run(install, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"NSSM {display} fehlgeschlagen: {result.stderr.strip()}")
            return False
        subprocess.run([nssm, "set", display, "AppDirectory", str(DestinyPaths.root())], check=False)
        subprocess.run([nssm, "start", display], check=False)
        print(f"NSSM-Service {display} erstellt")
        return True

    def _enable(self, service: str, linux_unit: str):
        print(self.svc.start(service))
        if DestinyPaths.is_windows():
            if shutil.which("nssm"):
                self.enable_nssm_service(service)
            else:
                print(f"Persistenz optional: enable_windows_persistence('{service}')")
        else:
            self._linux_service(linux_unit)

    def enable_self_healing(self):
        self._enable("watchdog", "destiny_watchdog.service")
        print("Self-Healing aktiviert.")

    def enable_auto_backup(self):
        self._enable("backup", "destiny_backup.service")
        print("Auto-Backup aktiviert.")

    def enable_voice(self):
        self._enable("voice", "destiny_voice.service")
        print("Voice Commander aktiviert.")

    def enable_monitor(self):
        self._enable("monitor", "destiny_monitor.service")
        print("Monitoring aktiviert.")

    def activate(self, name: str):
        fn = self.modules.get(name)
        if not fn:
            print(f"Unbekanntes Modul: {name}")
            return
        fn()
