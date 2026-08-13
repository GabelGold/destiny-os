#!/usr/bin/env python3
"""
Destiny Service Manager – einheitliche Steuerung (start/stop/status/list).
Windows: Prozess + PID-Datei. Linux: systemctl, Fallback Prozess.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from destiny_paths import DestinyPaths

SERVICES: Dict[str, dict] = {
    "core": {
        "script": "destiny_manager.py",
        "module": ["destiny_manager.py"],
        "port": None,
        "description": "Kernlogik",
        "unit": "destiny_core.service",
    },
    "gui": {
        "script": "destiny_gui.py",
        "module": ["-m", "streamlit", "run", "destiny_gui.py", "--server.headless", "true"],
        "port": 8501,
        "description": "Streamlit-GUI",
        "unit": "destiny_gui.service",
    },
    "monitor": {
        "script": "destiny_monitor.py",
        "module": ["destiny_monitor.py"],
        "port": None,
        "description": "System-Monitoring",
        "unit": "destiny_monitor.service",
    },
    "backup": {
        "script": "destiny_backup_agent.py",
        "module": ["destiny_backup_agent.py"],
        "port": None,
        "description": "Backup-Agent",
        "unit": "destiny_backup.service",
    },
    "advisor": {
        "script": "destiny_advisor.py",
        "module": ["destiny_advisor.py"],
        "port": None,
        "description": "Log-Berater",
        "unit": "destiny_advisor.service",
    },
    "listener": {
        "script": "destiny_session_listener.py",
        "module": ["destiny_session_listener.py"],
        "port": None,
        "description": "Session-Listener",
        "unit": "destiny_listener.service",
    },
    "voice": {
        "script": "voice_commander.py",
        "module": ["voice_commander.py"],
        "port": None,
        "description": "Voice Commander",
        "unit": "destiny_voice.service",
    },
    "watchdog": {
        "script": "destiny_watchdog.py",
        "module": ["destiny_watchdog.py"],
        "port": None,
        "description": "Watchdog",
        "unit": "destiny_watchdog.service",
    },
    "commander": {
        "script": "destiny_commander.py",
        "module": ["destiny_commander.py"],
        "port": DestinyPaths.commander_port(),
        "description": "Commander (Inbox + HTTP)",
        "unit": "destiny_commander.service",
    },
}


def port_open(port: int, host: str = "127.0.0.1") -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.4)
    try:
        return sock.connect_ex((host, port)) == 0
    finally:
        sock.close()


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if DestinyPaths.is_windows():
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
        )
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


class DestinyServiceManager:
    def __init__(self):
        self.services = SERVICES
        DestinyPaths.ensure()

    def pid_file(self, service: str) -> Path:
        return DestinyPaths.pid_dir() / f"{service}.pid"

    def command_for(self, service: str) -> List[str]:
        info = self.services[service]
        py = DestinyPaths.python()
        src = DestinyPaths.src()
        parts = list(info["module"])
        if parts[:2] == ["-m", "streamlit"]:
            script = str(src / parts[2])
            return [py, "-m", "streamlit", "run", script] + parts[3:]
        return [py, str(src / parts[0])]

    def start(self, service: str) -> str:
        if service not in self.services:
            return f"Service {service} nicht gefunden"
        current = self.status(service)
        if current.startswith("RUNNING"):
            return f"{service} laeuft bereits"
        if DestinyPaths.is_linux():
            unit = self.services[service]["unit"]
            done = subprocess.run(["systemctl", "start", unit], capture_output=True, text=True)
            if done.returncode == 0:
                return f"{service} gestartet (systemd)"
        cmd = self.command_for(service)
        proc = subprocess.Popen(cmd, cwd=str(DestinyPaths.root()))
        self.pid_file(service).write_text(str(proc.pid), encoding="utf-8")
        return f"{service} gestartet (pid {proc.pid})"

    def stop(self, service: str) -> str:
        if service not in self.services:
            return f"Service {service} nicht gefunden"
        if DestinyPaths.is_linux():
            subprocess.run(
                ["systemctl", "stop", self.services[service]["unit"]],
                capture_output=True,
            )
        pid = self._read_pid(service)
        if pid and pid_alive(pid):
            if DestinyPaths.is_windows():
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
            else:
                try:
                    os.kill(pid, 15)
                except OSError:
                    pass
        pf = self.pid_file(service)
        if pf.exists():
            pf.unlink()
        return f"{service} gestoppt"

    def _read_pid(self, service: str) -> Optional[int]:
        pf = self.pid_file(service)
        if not pf.exists():
            return None
        try:
            return int(pf.read_text(encoding="utf-8").strip())
        except ValueError:
            return None

    def status(self, service: str) -> str:
        if service not in self.services:
            return f"UNKNOWN {service}"
        info = self.services[service]
        port = info.get("port")
        if port and port_open(int(port)):
            return "RUNNING"
        pid = self._read_pid(service)
        if pid and pid_alive(pid):
            return "RUNNING"
        if DestinyPaths.is_linux():
            result = subprocess.run(
                ["systemctl", "is-active", info["unit"]],
                capture_output=True,
                text=True,
            )
            if result.stdout.strip() == "active":
                return "RUNNING"
        return "STOPPED"

    def snapshot(self) -> Dict[str, dict]:
        out = {}
        for name, info in self.services.items():
            out[name] = {
                "status": self.status(name),
                "description": info["description"],
                "script": info["script"],
                "port": info["port"],
            }
        return out

    def list_all(self) -> List[str]:
        lines = []
        for name, info in self.snapshot().items():
            mark = "RUNNING" if info["status"] == "RUNNING" else "STOPPED"
            lines.append(f"{mark} {name} - {info['description']}")
        return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop", "status", "list"])
    parser.add_argument("service", nargs="?", default=None)
    args = parser.parse_args()
    mgr = DestinyServiceManager()
    if args.action == "list":
        for line in mgr.list_all():
            print(line)
    elif not args.service:
        print("Bitte Service angeben")
        sys.exit(2)
    elif args.action == "start":
        print(mgr.start(args.service))
    elif args.action == "stop":
        print(mgr.stop(args.service))
    elif args.action == "status":
        print(f"{args.service}: {mgr.status(args.service)}")
