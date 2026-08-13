#!/usr/bin/env python3
"""
Destiny Watchdog – Restart nur bei Health-Check-Fehler, mit Limit und Backoff.
"""

from __future__ import annotations

import time
from typing import Dict

from destiny_paths import DestinyPaths
from destiny_service_manager import DestinyServiceManager, port_open

CHECK_INTERVAL = 60
MAX_RESTARTS = 3
RESTART_WINDOW = 300


class DestinyWatchdog:
    def __init__(self):
        self.manager = DestinyServiceManager()
        self.services = ["core", "gui", "monitor", "backup"]
        self.max_restarts = MAX_RESTARTS
        self.restart_window = RESTART_WINDOW
        self.restart_counts: Dict[str, int] = {}
        self.last_restart_time: Dict[str, float] = {}

    def check_health(self, service: str) -> bool:
        try:
            if service == "core":
                from destiny_manager import DestinyManager

                status = DestinyManager().health_check()
                return status.get("status") in ("healthy", "recovered")
            if service == "gui":
                return port_open(8501)
            return self.manager.status(service) == "RUNNING"
        except Exception as exc:
            print(f"Health-Check {service} fehlgeschlagen: {exc}")
            return False

    def restart_service(self, service: str) -> bool:
        now = time.time()
        last = self.last_restart_time.get(service, 0)
        if now - last > self.restart_window:
            self.restart_counts[service] = 0
        count = self.restart_counts.get(service, 0)
        if count >= self.max_restarts:
            print(f"{service}: Max Restarts erreicht ({self.max_restarts} / {self.restart_window}s)")
            return False
        print(f"Restart {service} (Versuch {count + 1}/{self.max_restarts})")
        self.manager.stop(service)
        time.sleep(min(8, 2 ** count))
        print(self.manager.start(service))
        self.restart_counts[service] = count + 1
        self.last_restart_time[service] = now
        return True

    def run(self, once: bool = False, interval: int = CHECK_INTERVAL):
        print("Destiny Watchdog gestartet")
        while True:
            for service in self.services:
                if self.check_health(service):
                    continue
                print(f"{service} nicht healthy")
                self.restart_service(service)
            if once:
                return
            time.sleep(interval)


def health_check() -> bool:
    """Kompatibilität: Gesamt-Health über den Manager."""
    try:
        from destiny_manager import DestinyManager

        status = DestinyManager().health_check()
        return status.get("status") in ("healthy", "recovered")
    except Exception as exc:
        print(f"Health-Check fehlgeschlagen: {exc}")
        return False


def main():
    DestinyWatchdog().run()


if __name__ == "__main__":
    main()
